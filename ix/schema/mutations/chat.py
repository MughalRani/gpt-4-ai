import logging
import graphene

from ix.schema.types.messages import TaskLogMessageType
from ix.schema.utils import handle_exceptions
from ix.task_log.models import TaskLogMessage, UserFeedback
from ix.task_log.tasks.agent_runner import (
    start_agent_loop,
)


logger = logging.getLogger(__name__)


class TaskLogResponseInput(graphene.InputObjectType):
    id = graphene.String(required=True)
    response = graphene.String(required=True)
    is_authorized = graphene.Boolean(required=True)


class TaskLogMessageResponse(graphene.ObjectType):
    task_log_message = graphene.Field(TaskLogMessage)
    errors = graphene.List(graphene.String)

    def resolve_task_log(root, info):
        return root.task_log


class RespondToTaskLogMutation(graphene.Mutation):
    class Arguments:
        input = TaskLogResponseInput(required=True)

    task_log_message = graphene.Field(TaskLogMessageType)
    errors = graphene.Field(graphene.List(graphene.String))

    @staticmethod
    @handle_exceptions
    def mutate(root, info, input):
        # save to persistent storage
        responding_to = TaskLogMessage.objects.get(pk=input.id)
        message = TaskLogMessage.objects.create(
            task_id=responding_to.task_id,
            role="USER",
            content=UserFeedback(
                type="FEEDBACK",
                feedback=input.response,
            ),
        )

        # resume task loop
        logger.info(
            f"Requesting agent loop resume task_id={message.task_id} message_id={message.pk}"
        )

        # Start agent loop. This does NOT check if the loop is already running
        # the agent_runner task is responsible for blocking duplicate runners
        start_agent_loop.delay(responding_to.task_id)

        return TaskLogMessageResponse(task_log_message=message)
