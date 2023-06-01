import logging
import json
from typing import Dict, List, Any
from jsonpath_ng import parse as jsonpath_parse
from langchain.chains.base import Chain

from ix.agents.callback_manager import IxCallbackManager
from ix.commands.filesystem import write_to_file
from ix.task_log.models import Artifact, TaskLogMessage


logger = logging.getLogger(__name__)


class SaveArtifact(Chain):
    """
    Save an artifact to the database.

    This chain is used to save an artifact to the database. It can be used to
    save an artifact that was generated by a prior step in the chain, or to
    save an artifact from an arbitrary object type.

    To save an artifact that was generated by a prior step in the chain, set
    the `artifact_from_key` to the key of the artifact in the input.

    To save an artifact from an arbitrary object type, set the `artifact_key`

    `artifact_storage` is always set from the config for now. The artifact storage
    is used to determine how the artifact is stored. For example, if the storage
    is set to `write_to_file`, the artifact will be stored in the filesystem.

    `artifact_type` is used to determine how the artifact may be used and displayed.
    This property must be set in the config.
    """

    # indicates artifact is available in the input
    artifact_from_key: str = None

    # values to use to create an artifact
    artifact_key: str = None
    artifact_type: str = None
    artifact_name: str = None
    artifact_description: str = None
    artifact_storage: str = None
    artifact_storage_id: str = None

    # intput / output mapping
    content_key: str = "content"
    content_path: str = None
    output_key: str = "artifact_id"

    @property
    def _chain_type(self) -> str:
        return "ix.save_artifact"  # pragma: no cover

    @property
    def input_keys(self) -> List[str]:
        keys = []
        if self.artifact_from_key:
            keys.append(self.artifact_from_key)
        logger.debug(f"KEYS: {keys}")
        return keys

    @property
    def output_keys(self) -> List[str]:
        return [self.output_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        if self.artifact_from_key:
            # load artifact from input key. Use this when a prior step
            # generated the artifact object
            artifact = inputs.get(self.artifact_from_key, {}).copy()
        else:
            # generating an artifact using only the config
            # use this when the artifact is generated in this step
            artifact = {
                "key": self.artifact_key,
                "name": self.artifact_name,
                "description": self.artifact_description,
                "identifier": f"{self.artifact_key}_{self.callbacks.think_msg.id}",
            }

        # Storage is always set from the config for now
        if self.artifact_storage:
            artifact["storage"] = {
                "type": self.artifact_storage,
                "id": self.artifact_storage_id or artifact["identifier"],
            }
        if self.artifact_type:
            artifact["artifact_type"] = self.artifact_type

        # extract content from input
        # default path to the content key.
        jsonpath_expr = jsonpath_parse(self.content_path or self.content_key)
        json_matches = jsonpath_expr.find(inputs)
        content = json_matches[0].value

        # Associate the artifact with the parent task (chat) until
        # frontend API call can include artifacts from any descendant
        # of the Chat's task.
        task = self.callbacks.task
        artifact_task_id = task.parent_id if task.parent_id else task.id

        # save to artifact storage
        artifact = Artifact.objects.create(
            task_id=artifact_task_id,
            key=artifact["key"] or artifact["identifier"],
            name=artifact["name"],
            description=artifact["description"],
            artifact_type=artifact["artifact_type"],
            storage=artifact["storage"],
        )

        # send message to log
        TaskLogMessage.objects.create(
            role="assistant",
            task=self.callbacks.task,
            agent=self.callbacks.task.agent,
            parent=self.callbacks.think_msg,
            content={
                "type": "ARTIFACT",
                "artifact_type": artifact.artifact_type,
                "artifact_id": str(artifact.id),
                "storage": artifact.storage,
                "description": artifact.description,
                # TODO: store on message until frontend has subscription to artifacts
                "data": content,
            },
        )

        # write to storage (i.e. file, database, or a cache)
        if self.artifact_storage == "write_to_file":
            file_path = artifact.storage["id"]
            logger.debug(f"writing content to file file_path={file_path} {content}")
            if not isinstance(content, str):
                content = json.dumps(content)
            write_to_file(file_path, content)

        return {self.output_key: str(artifact.id)}

    async def _acall(self, inputs: Dict[str, str]) -> Dict[str, str]:
        pass  # pragma: no cover

    @classmethod
    def from_config(cls, config: Dict[str, Any], callback_manager: IxCallbackManager):
        return cls(**config, callbacks=callback_manager)
