# iX - Autonomous GPT-4 Agent Platform

<div>
<img align="left" src="ix_350.png" alt="The ninth planet around the sun">
<p>
<br>
<br>
<br>
<br>
Amidst the swirling sands of the cosmos, Ix stands as an enigmatic jewel, 
where the brilliance of human ingenuity dances on the edge of forbidden 
knowledge, casting a shadow of intrigue over the galaxy.

\- Atreides Scribe, The Chronicles of Ixian Innovation
<p>
</div>
<div>
<br>
<br>
<br>
<br>
<br>
</div>


## About
<div>
iX is a platform to run semi-autonomous GPT-4 agents, providing a scalable and responsive solution for delegating tasks.
Agents can be spawned as individual processes to research and complete tasks through a web based interface while the 
backend architecture efficiently manages message queues and inter-agent communication between a fleet of workers.
<br>
<br>
The platform supports deployment using Docker containers, ensuring a consistent environment and enabling easy scaling 
to multiple worker containers.
</div>

## How does it work

You provide a task and goals and an agent uses that direction to investigate, plan, and complete tasks. The agents are
capable of searching the web, writing code, creating images, interacting with other APIs and services. If it can be 
coded, it's within the realm of possibility for an agent to assist.

![Dialog for entering task name and goals](docs/create_task.png)
![chat interface displaying log](docs/chat.png)

**Note that this is an early version and should NOT be used in production. Agents require a human in the loop to provide
direction and halt the process if it goes off the rails.**

## Key Features

- Scalable model for running a fleet of GPT agents.
- Persistent storage of interactions, processes, and metrics.
- Responsive user interface.
- Message queue for agent jobs and inter-agent communication.
- Extensible model for customizing agents.
- Deployment using Docker.


## Technologies:
- Python 3.11
- Django 4.2
- PostgreSQL 14.4
- Graphql
- React 18
- Integrated with OpenAI GPT models
- Plugin architecture to support extending agent functionality (e.g. web browsing, writing code, etc)
- Generic framework for vector database based agent memory
    - Pinecone
    - Redis
    - Milvus (soon)
    - FAISS (soon)

## Prerequisites

Before getting started, ensure you have the following software installed on your system:

- Docker
- Docker Compose

## Setup

Clone the repository:

```bash
git clone https://github.com/kreneskyp/ix.git
cd ix
```

Setup config in `.env`

```bash
cp .env.template .env
```

```
OPENAI_API_KEY=YOUR_KEY_HERE

# Pinecone
PINECONE_API_KEY=
PINECONE_ENV=

# search
GOOGLE_API_KEY=
GOOGLE_CX_ID=
WOLFRAM_APP_ID=
```


Build and run the dev image.

```
make dev_setup
```

Run the dev server

```bash
make runserver
```

Start a worker
```bash
make worker
```


## Usage

Visit `http://localhost:8000` to access the user interface and start creating tasks for the autonomous GPT-4 agents. 
The platform will automatically spawn agent processes to research and complete tasks as needed.


### Scaling workers
Run as many worker processes as you want with `make worker`.


## Developer Tools

Here are some helpful commands for developers to set up and manage the development environment:

### Running:
- `make runserver`: Start the application in development mode on `0.0.0.0:8000`.
- `make worker`: Start an Agent worker.

### Building:
- `make image`: Build the Docker image.
- `make frontend`: Rebuild the front end (graphql, relay, webpack).
- `make webpack`: Rebuild javascript only
- `make webpack-watch`: Rebuild javascript on file changes

### Database
- `make migrate`: Run Django database migrations.
- `make migrations`: Generate new Django database migration files.

### Utility
- `make bash`: Open a bash shell in the docker container.
- `make shell`: Open a Django shell_plus session.
