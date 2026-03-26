// PawPal+ Final Class Diagram (Mermaid.js)
// Paste the diagram below into https://mermaid.live to preview

/*
classDiagram
    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String frequency
        +bool completed
        +Date due_date
        +String start_time
        +priority_value() int
        +mark_complete()
        +mark_incomplete()
        +next_occurrence() Task
    }
    class Pet {
        +String name
        +String species
        +List tasks
        +add_task(task)
        +remove_task(title)
        +pending_tasks() List
        +complete_task(title)
    }
    class Owner {
        +String name
        +int available_minutes
        +List pets
        +add_pet(pet)
        +remove_pet(name)
        +get_all_tasks() List
        +get_pending_tasks() List
        +filter_tasks_by_pet(name) List
        +filter_tasks_by_status(completed) List
    }
    class Schedule {
        +List planned_tasks
        +List skipped_tasks
        +int total_duration
        +summary() String
    }
    class Scheduler {
        +Owner owner
        +get_tasks() List
        +sort_by_time(tasks) List
        +detect_conflicts(tasks) List
        +generate() Schedule
        +_time_to_minutes(time_str) int
    }

    Owner "1" --> "many" Pet : manages
    Pet "1" --> "many" Task : owns
    Scheduler --> Owner : reads from
    Scheduler --> Schedule : produces
    Schedule "1" --> "many" Task : contains
    Task --> Task : next_occurrence()
*/
