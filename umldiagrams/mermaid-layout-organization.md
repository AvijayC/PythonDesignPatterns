# Mermaid Diagram Layout & Organization Guide

## Table of Contents
1. [Basic Direction Control](#basic-direction-control)
2. [Node Positioning Strategies](#node-positioning-strategies)
3. [Subgraphs for Layering](#subgraphs-for-layering)
4. [Advanced Layout Techniques](#advanced-layout-techniques)
5. [Common Layout Patterns](#common-layout-patterns)
6. [Tips & Best Practices](#tips--best-practices)

## Basic Direction Control

Mermaid provides four primary flow directions that control how your diagram grows:

### Flow Directions

```mermaid
graph TB
    A[Top to Bottom - TB/TD]
```

```mermaid
graph LR
    A[Left to Right - LR]
```

```mermaid
graph BT
    A[Bottom to Top - BT]
```

```mermaid
graph RL
    A[Right to Left - RL]
```

### Direction Examples

#### Top-Down (TB or TD) - Default
```mermaid
graph TD
    Start[Start Process]
    Start --> Step1[Step 1]
    Step1 --> Step2[Step 2]
    Step2 --> Decision{Decision?}
    Decision -->|Yes| Result1[Result A]
    Decision -->|No| Result2[Result B]
```

#### Left-Right (LR) - Horizontal Flow
```mermaid
graph LR
    Input[Input] --> Process[Process Data]
    Process --> Transform[Transform]
    Transform --> Output[Output]
```

## Node Positioning Strategies

### 1. Invisible Nodes for Spacing

Use invisible nodes to create space and control layout:

```mermaid
graph TD
    A[Node A]
    A --> B[Node B]
    A --> invisible1[ ]
    invisible1 --> C[Node C]
    
    style invisible1 fill:transparent,stroke:transparent
```

### 2. Link Lengths for Distance Control

Use different arrow styles to imply distance:

```mermaid
graph LR
    A[Start] --> B[Near]
    A -.-> C[Medium]
    A ==> D[Far/Important]
    A --> E[Regular]
```

### 3. Explicit Ordering with Sequential Connections

Force nodes to appear in specific order:

```mermaid
graph TD
    subgraph "Forced Ordering"
        A1[First] --> A2[Second]
        A2 --> A3[Third]
        A3 --> A4[Fourth]
    end
    
    subgraph "Natural Flow"
        B1[Node 1]
        B2[Node 2]
        B3[Node 3]
        B1 --> B2
        B1 --> B3
    end
```

## Subgraphs for Layering

Subgraphs are the primary way to create visual layers and groupings:

### Basic Subgraph Layers

```mermaid
graph TD
    subgraph "Layer 1 - Presentation"
        UI1[Web UI]
        UI2[Mobile App]
        UI3[API Client]
    end
    
    subgraph "Layer 2 - Business Logic"
        BL1[Service A]
        BL2[Service B]
        BL3[Service C]
    end
    
    subgraph "Layer 3 - Data Layer"
        DB1[(Database)]
        DB2[(Cache)]
        DB3[(File Storage)]
    end
    
    UI1 --> BL1
    UI2 --> BL2
    UI3 --> BL3
    BL1 --> DB1
    BL2 --> DB2
    BL3 --> DB3
```

### Nested Subgraphs for Hierarchy

```mermaid
graph TB
    subgraph "System"
        subgraph "Frontend"
            A[React App]
            B[Vue App]
        end
        
        subgraph "Backend"
            subgraph "Services"
                C[Auth Service]
                D[Data Service]
            end
            subgraph "Infrastructure"
                E[(Database)]
                F[Cache]
            end
        end
    end
    
    A --> C
    B --> D
    C --> E
    D --> F
```

### Side-by-Side Subgraphs

```mermaid
graph LR
    subgraph "Development"
        Dev1[Code]
        Dev2[Test]
        Dev1 --> Dev2
    end
    
    subgraph "Staging"
        Stage1[Deploy]
        Stage2[Validate]
        Stage1 --> Stage2
    end
    
    subgraph "Production"
        Prod1[Release]
        Prod2[Monitor]
        Prod1 --> Prod2
    end
    
    Dev2 --> Stage1
    Stage2 --> Prod1
```

## Advanced Layout Techniques

### 1. Rank Alignment (Simulating GraphViz Ranks)

While Mermaid doesn't have explicit rank control like GraphViz, you can simulate it:

```mermaid
graph TD
    %% Rank 1 - Top Level
    Start[Start]
    
    %% Rank 2 - Processing Level
    Start --> Process1[Process 1]
    Start --> Process2[Process 2]
    Start --> Process3[Process 3]
    
    %% Force alignment by connecting to invisible node
    Process1 --> Invisible1[ ]
    Process2 --> Invisible1
    Process3 --> Invisible1
    
    %% Rank 3 - Results Level
    Invisible1 --> Result[Combined Result]
    
    style Invisible1 fill:transparent,stroke:transparent
```

### 2. Diamond/Rhombus Layouts

Create diamond patterns for decision trees:

```mermaid
graph TD
    Top[Top Node]
    Top --> Left[Left Branch]
    Top --> Right[Right Branch]
    Left --> Bottom[Merge Point]
    Right --> Bottom
    Bottom --> Final[Final Node]
```

### 3. Matrix/Grid Layout

Simulate a grid using subgraphs and careful connections:

```mermaid
graph TD
    subgraph "Row 1"
        A1[1,1] ---|col| A2[1,2]
        A2 ---|col| A3[1,3]
    end
    
    subgraph "Row 2"
        B1[2,1] ---|col| B2[2,2]
        B2 ---|col| B3[2,3]
    end
    
    subgraph "Row 3"
        C1[3,1] ---|col| C2[3,2]
        C2 ---|col| C3[3,3]
    end
    
    A1 ---|row| B1
    B1 ---|row| C1
    A2 ---|row| B2
    B2 ---|row| C2
    A3 ---|row| B3
    B3 ---|row| C3
```

### 4. Circular/Radial Layout (Simulated)

While Mermaid doesn't support true circular layouts, you can approximate:

```mermaid
graph TD
    Center[Core]
    Center --> N[North]
    Center --> E[East]
    Center --> S[South]
    Center --> W[West]
    Center --> NE[NorthEast]
    Center --> SE[SouthEast]
    Center --> SW[SouthWest]
    Center --> NW[NorthWest]
```

## Common Layout Patterns

### 1. Three-Tier Architecture

```mermaid
graph TD
    subgraph "Presentation Tier"
        Web[Web Server]
        Mobile[Mobile App]
    end
    
    subgraph "Application Tier"
        API[API Gateway]
        Service1[Service 1]
        Service2[Service 2]
    end
    
    subgraph "Data Tier"
        DB[(Primary DB)]
        Cache[(Redis Cache)]
    end
    
    Web --> API
    Mobile --> API
    API --> Service1
    API --> Service2
    Service1 --> DB
    Service2 --> Cache
```

### 2. Pipeline/Workflow Pattern

```mermaid
graph LR
    subgraph "Stage 1: Input"
        Input1[Source A]
        Input2[Source B]
    end
    
    subgraph "Stage 2: Process"
        Process[Data Processing]
    end
    
    subgraph "Stage 3: Transform"
        Transform[Transformation]
    end
    
    subgraph "Stage 4: Output"
        Output1[Destination A]
        Output2[Destination B]
    end
    
    Input1 --> Process
    Input2 --> Process
    Process --> Transform
    Transform --> Output1
    Transform --> Output2
```

### 3. Hub and Spoke Pattern

```mermaid
graph TD
    Hub[Central Hub]
    
    subgraph "Spokes"
        Spoke1[System A]
        Spoke2[System B]
        Spoke3[System C]
        Spoke4[System D]
    end
    
    Spoke1 <--> Hub
    Spoke2 <--> Hub
    Spoke3 <--> Hub
    Spoke4 <--> Hub
```

### 4. Hierarchical Tree

```mermaid
graph TD
    CEO[CEO]
    CEO --> CTO[CTO]
    CEO --> CFO[CFO]
    CEO --> COO[COO]
    
    CTO --> Dev[Dev Team]
    CTO --> QA[QA Team]
    
    CFO --> Accounting[Accounting]
    CFO --> Finance[Finance]
    
    COO --> Operations[Operations]
    COO --> HR[HR]
```

## Tips & Best Practices

### 1. Use Comments for Organization

```mermaid
graph TD
    %% Input Layer
    Input[User Input]
    
    %% Processing Layer
    Input --> Validate[Validation]
    Validate --> Process[Processing]
    
    %% Output Layer
    Process --> Format[Format Output]
    Format --> Display[Display Result]
```

### 2. Consistent Node Naming Convention

```mermaid
graph LR
    %% Use prefixes for different layers
    UI_Login[Login Page]
    UI_Dashboard[Dashboard]
    
    API_Auth[Auth API]
    API_Data[Data API]
    
    DB_Users[(Users DB)]
    DB_Sessions[(Sessions DB)]
    
    UI_Login --> API_Auth
    UI_Dashboard --> API_Data
    API_Auth --> DB_Users
    API_Auth --> DB_Sessions
```

### 3. Color Coding for Visual Hierarchy

```mermaid
graph TD
    A[Input]:::input
    B[Process]:::process
    C[Output]:::output
    
    A --> B --> C
    
    classDef input fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef process fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef output fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
```

### 4. Link Styling for Importance

```mermaid
graph LR
    A[Start] ==>|Critical Path| B[Important]
    A -->|Normal Path| C[Regular]
    A -.->|Optional Path| D[Optional]
    
    style B fill:#ff9999,stroke:#ff0000,stroke-width:3px
```

### 5. Managing Complex Diagrams

For very complex diagrams:

1. **Break into multiple diagrams**: Instead of one huge diagram, create several focused ones
2. **Use subgraphs liberally**: Group related nodes
3. **Consider direction changes**: Mix TB and LR in different subgraphs
4. **Use consistent spacing**: Add invisible nodes for alignment
5. **Minimize crossing lines**: Reorder nodes to reduce line crossings

### Example: Complex System with Multiple Techniques

```mermaid
graph TB
    subgraph "User Layer"
        direction LR
        User1[Desktop Users]
        User2[Mobile Users]
        User3[API Clients]
    end
    
    subgraph "Gateway Layer"
        direction LR
        GW[API Gateway]
        LB[Load Balancer]
    end
    
    subgraph "Service Layer"
        direction LR
        Auth[Auth Service]
        Data[Data Service]
        Process[Process Service]
    end
    
    subgraph "Data Layer"
        direction LR
        Primary[(Primary DB)]
        Replica[(Replica DB)]
        Cache[(Cache)]
    end
    
    User1 --> GW
    User2 --> GW
    User3 --> GW
    
    GW --> LB
    
    LB --> Auth
    LB --> Data
    LB --> Process
    
    Auth --> Cache
    Data --> Primary
    Data --> Replica
    Process --> Primary
    
    Primary -.->|Replication| Replica
    
    classDef userNode fill:#e3f2fd,stroke:#1565c0
    classDef serviceNode fill:#fff3e0,stroke:#ef6c00
    classDef dataNode fill:#f3e5f5,stroke:#6a1b9a
    
    class User1,User2,User3 userNode
    class Auth,Data,Process serviceNode
    class Primary,Replica,Cache dataNode
```

## Limitations and Workarounds

### What Mermaid Can't Do (and Workarounds)

1. **True rank-based layouts** (like GraphViz's rank=same)
   - Workaround: Use subgraphs and invisible nodes

2. **Precise node positioning** (x,y coordinates)
   - Workaround: Use directional flow and subgraphs strategically

3. **Circular/radial layouts**
   - Workaround: Manually arrange nodes in approximate circle

4. **Orthogonal edge routing** (only straight lines at 90°)
   - Workaround: Use intermediate invisible nodes

5. **Node alignment across subgraphs**
   - Workaround: Connect to shared invisible nodes

## Comparison with GraphViz

| Feature | GraphViz | Mermaid | Mermaid Workaround |
|---------|----------|---------|-------------------|
| Rank control | `rank=same` | ❌ | Use subgraphs |
| Precise positioning | `pos="x,y"` | ❌ | Strategic connections |
| Multiple layout engines | dot, neato, fdp, etc. | ❌ | Use direction changes |
| Constraint control | `constraint=false` | ❌ | Use different arrow types |
| Cluster ranking | ✅ | Partial | Nested subgraphs |
| Edge routing | Multiple options | Limited | Invisible nodes |

## Best Practices Summary

1. **Start with the right direction** (TB, LR, BT, RL)
2. **Use subgraphs** to create visual layers and groupings
3. **Leverage invisible nodes** for spacing and alignment
4. **Apply consistent naming** conventions with prefixes
5. **Use color coding** to enhance visual hierarchy
6. **Break complex diagrams** into smaller, focused ones
7. **Comment your diagram** code for maintainability
8. **Test different layouts** to find the best visualization

Remember: While Mermaid may not have all of GraphViz's advanced layout features, its simplicity and integration with Markdown make it excellent for documentation and quick visualizations. The key is understanding its limitations and working creatively within them.