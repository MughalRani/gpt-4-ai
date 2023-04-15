from celery import shared_task

from ix.agents.process import AgentProcess
from ix.task_log.models import TaskLogMessage


@shared_task
def start_agent_loop(task_id: int):
    """
    Start agent process loop
    """
    process = AgentProcess(task_id=task_id)
    return process.start()
