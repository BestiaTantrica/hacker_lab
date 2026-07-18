#!/bin/bash
export PATH=$PATH:/home/tomas2/bin

echo "============================================================"
echo "  CREADOR AUTOMÁTICO DE OCI-2 (REINTENTO INTELIGENTE)"
echo "============================================================"

TENANCY=$(grep tenancy ~/.oci/config | cut -d'=' -f2)
COMPARTMENT=$(oci iam compartment list -c $TENANCY --query "data[?\"lifecycle-state\"=='ACTIVE'].id | [0]" --raw-output 2>/dev/null)
if [ -z "$COMPARTMENT" ] || [ "$COMPARTMENT" == "null" ]; then COMPARTMENT=$TENANCY; fi

SUBNET=$(oci network subnet list -c $COMPARTMENT --query "data[0].id" --raw-output)
IMAGE=$(oci compute image list -c $COMPARTMENT --operating-system "Canonical Ubuntu" --operating-system-version "24.04" --shape "VM.Standard.E2.1.Micro" --query "data[0].id" --raw-output)

# Obtener todos los dominios de disponibilidad (AD-1, AD-2, AD-3)
ADS=$(oci iam availability-domain list -c $COMPARTMENT --query "data[*].name" --raw-output | tr -d '[]," ' | sed '/^$/d')

EXITO=0
for AD in $ADS; do
    echo "🚀 Intentando lanzar Instancia Micro en: $AD"
    
    # Redirigir el error estandar a un archivo para que no ensucie la pantalla si falla
    oci compute instance launch \
      --availability-domain "$AD" \
      --compartment-id "$COMPARTMENT" \
      --shape "VM.Standard.E2.1.Micro" \
      --display-name "OCI-2-Cerebro" \
      --image-id "$IMAGE" \
      --subnet-id "$SUBNET" \
      --assign-public-ip true \
      --ssh-authorized-keys-file ~/.ssh/id_rsa.pub \
      --wait-for-state RUNNING 2>/tmp/oci_error.log
      
    if [ $? -eq 0 ]; then
        echo "✅ ¡Éxito en el dominio $AD!"
        EXITO=1
        break
    else
        echo "❌ Falló en $AD (Seguramente sin stock o sin permisos). Probando el siguiente..."
    fi
done

if [ $EXITO -eq 0 ]; then
    echo "🚨 Error crítico: No se pudo crear en ningún dominio. Detalle del último error:"
    cat /tmp/oci_error.log
    exit 1
fi

echo ""
echo "🎉 ¡Instancia Creada Exitosamente!"
INSTANCE_ID=$(oci compute instance list -c $COMPARTMENT --display-name "OCI-2-Cerebro" --query "data[0].id" --raw-output)
VNIC_ATTACHMENT=$(oci compute vnic-attachment list -c $COMPARTMENT --instance-id $INSTANCE_ID --query "data[0].id" --raw-output)
VNIC_ID=$(oci compute vnic-attachment get --vnic-attachment-id $VNIC_ATTACHMENT --query "data.\"vnic-id\"" --raw-output)
PUBLIC_IP=$(oci network vnic get --vnic-id $VNIC_ID --query "data.\"public-ip\"" --raw-output)

echo "============================================================"
echo "🎯 IP PÚBLICA DE OCI-2: $PUBLIC_IP"
echo "============================================================"
echo "Para conectarte usa: ssh -i ~/.ssh/id_rsa ubuntu@$PUBLIC_IP"
