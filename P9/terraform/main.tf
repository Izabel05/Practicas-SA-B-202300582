# El bootstrap completo de P9 se ejecuta desde bootstrap.tf después de crear
# el clúster. Los recursos Kubernetes no se gestionan con el provider
# kubernetes para evitar una conexión circular durante el primer apply.
