/**
 * @generated SignedSource<<b39ab412ee169d49f334b06ee67f6aa3>>
 * @lightSyntaxTransform
 * @nogrep
 */

/* eslint-disable */

'use strict';

var node = (function(){
var v0 = [
  {
    "defaultValue": null,
    "kind": "LocalArgument",
    "name": "taskId"
  }
],
v1 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "id",
  "storageKey": null
},
v2 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "type",
  "storageKey": null
},
v3 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "text",
  "storageKey": null
},
v4 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "name",
  "storageKey": null
},
v5 = {
  "alias": null,
  "args": null,
  "kind": "ScalarField",
  "name": "messageId",
  "storageKey": null
},
v6 = [
  (v2/*: any*/),
  (v5/*: any*/)
],
v7 = [
  {
    "alias": null,
    "args": [
      {
        "kind": "Variable",
        "name": "taskId",
        "variableName": "taskId"
      }
    ],
    "concreteType": "TaskLogMessageType",
    "kind": "LinkedField",
    "name": "taskLogMessages",
    "plural": true,
    "selections": [
      (v1/*: any*/),
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "role",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "kind": "ScalarField",
        "name": "createdAt",
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "concreteType": null,
        "kind": "LinkedField",
        "name": "content",
        "plural": false,
        "selections": [
          {
            "alias": null,
            "args": null,
            "kind": "ScalarField",
            "name": "__typename",
            "storageKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": [
              (v2/*: any*/),
              {
                "alias": null,
                "args": null,
                "concreteType": "ThoughtsType",
                "kind": "LinkedField",
                "name": "thoughts",
                "plural": false,
                "selections": [
                  (v3/*: any*/),
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "reasoning",
                    "storageKey": null
                  },
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "plan",
                    "storageKey": null
                  },
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "criticism",
                    "storageKey": null
                  },
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "speak",
                    "storageKey": null
                  }
                ],
                "storageKey": null
              },
              {
                "alias": null,
                "args": null,
                "concreteType": "CommandType",
                "kind": "LinkedField",
                "name": "command",
                "plural": false,
                "selections": [
                  (v4/*: any*/),
                  {
                    "alias": null,
                    "args": null,
                    "kind": "ScalarField",
                    "name": "args",
                    "storageKey": null
                  }
                ],
                "storageKey": null
              }
            ],
            "type": "AssistantContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": [
              (v2/*: any*/),
              {
                "alias": null,
                "args": null,
                "kind": "ScalarField",
                "name": "enabled",
                "storageKey": null
              }
            ],
            "type": "AutonomousModeContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": (v6/*: any*/),
            "type": "AuthorizeContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": (v6/*: any*/),
            "type": "AuthRequestContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": (v6/*: any*/),
            "type": "ExecutedContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": [
              (v2/*: any*/),
              (v5/*: any*/),
              {
                "alias": null,
                "args": null,
                "kind": "ScalarField",
                "name": "errorType",
                "storageKey": null
              },
              (v3/*: any*/)
            ],
            "type": "ExecuteErrorType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": [
              (v2/*: any*/),
              {
                "alias": null,
                "args": null,
                "kind": "ScalarField",
                "name": "feedback",
                "storageKey": null
              }
            ],
            "type": "FeedbackContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": (v6/*: any*/),
            "type": "FeedbackRequestContentType",
            "abstractKey": null
          },
          {
            "kind": "InlineFragment",
            "selections": [
              (v2/*: any*/),
              {
                "alias": null,
                "args": null,
                "kind": "ScalarField",
                "name": "message",
                "storageKey": null
              }
            ],
            "type": "SystemContentType",
            "abstractKey": null
          }
        ],
        "storageKey": null
      },
      {
        "alias": null,
        "args": null,
        "concreteType": "AgentType",
        "kind": "LinkedField",
        "name": "agent",
        "plural": false,
        "selections": [
          (v1/*: any*/),
          (v4/*: any*/)
        ],
        "storageKey": null
      }
    ],
    "storageKey": null
  }
];
return {
  "fragment": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Fragment",
    "metadata": null,
    "name": "TaskLogMessagesQuery",
    "selections": (v7/*: any*/),
    "type": "Query",
    "abstractKey": null
  },
  "kind": "Request",
  "operation": {
    "argumentDefinitions": (v0/*: any*/),
    "kind": "Operation",
    "name": "TaskLogMessagesQuery",
    "selections": (v7/*: any*/)
  },
  "params": {
    "cacheID": "e5f235215a3a4229f4c8925d6fbdf940",
    "id": null,
    "metadata": {},
    "name": "TaskLogMessagesQuery",
    "operationKind": "query",
    "text": "query TaskLogMessagesQuery(\n  $taskId: ID!\n) {\n  taskLogMessages(taskId: $taskId) {\n    id\n    role\n    createdAt\n    content {\n      __typename\n      ... on AssistantContentType {\n        type\n        thoughts {\n          text\n          reasoning\n          plan\n          criticism\n          speak\n        }\n        command {\n          name\n          args\n        }\n      }\n      ... on AutonomousModeContentType {\n        type\n        enabled\n      }\n      ... on AuthorizeContentType {\n        type\n        messageId\n      }\n      ... on AuthRequestContentType {\n        type\n        messageId\n      }\n      ... on ExecutedContentType {\n        type\n        messageId\n      }\n      ... on ExecuteErrorType {\n        type\n        messageId\n        errorType\n        text\n      }\n      ... on FeedbackContentType {\n        type\n        feedback\n      }\n      ... on FeedbackRequestContentType {\n        type\n        messageId\n      }\n      ... on SystemContentType {\n        type\n        message\n      }\n    }\n    agent {\n      id\n      name\n    }\n  }\n}\n"
  }
};
})();

node.hash = "4e2b7db9e1ff7e0386a00c03a59d5b26";

module.exports = node;
