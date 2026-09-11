# Diagrama del pipeline CI/CD

![alt text](<Diagrama -FlujoPipeline.png>)

El grafo ejecutado por GitHub Actions sigue estas dependencias:

```mermaid
flowchart LR
    A[0 - Preparacion y version] --> B[1 - Build Go]
    A --> C[1 - Build Python]
    B --> D[2 - Pruebas Go]
    C --> E[2 - Pruebas Python]
    D --> F[3 - Matriz Docker: 6 imagenes]
    E --> F
    F --> G[4 - Despliegue GKE con Helm]
    G --> H[5 - Smoke tests GKE]
```

Las matrices agrupan varios jobs equivalentes dentro de una sola caja visual. El
job de preparacion tambien falla si la seleccion deja de contener exactamente
nueve pruebas: siete unitarias y dos de integracion.
