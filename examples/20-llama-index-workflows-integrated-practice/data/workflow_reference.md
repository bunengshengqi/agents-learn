# Day20 Workflow Reference

## Workflow

LlamaIndex Workflow is an event-driven orchestration system. A workflow starts with StartEvent, passes custom Event objects between steps, and finishes with StopEvent.

## Step

A step is an async function marked with @step. Its input and output type hints are part of the workflow graph. If a step receives QueryEvent and returns DocsEvent, LlamaIndex knows how to connect it.

## Event

An Event is a typed data packet. It carries information between steps, such as query, documents, retry_count, selected_route, and trace.

## Context

Context stores shared state during one workflow run. Use await ctx.store.set(key, value) and await ctx.store.get(key). It is useful for traces, counters, original query, retrieved sources, and intermediate results.

## Branch

A branch is created when one step returns different Event types based on conditions. For example, a router can return RAGEvent, PricingEvent, BugEvent, or DirectAnswerEvent.

## Loop

A loop is created when a step returns an Event that triggers a previous step again. RAG often uses loops: retrieve, evaluate, rewrite query, retrieve again, and stop when enough context is found.

## Fan-out Fan-in

Fan-out means splitting one task into several parallel subtasks. Fan-in means collecting the results. This is useful when searching multiple sources such as Obsidian notes, course notes, and code snippets.

## RAG

RAG means retrieval augmented generation. A workflow can implement RAG by normalizing the question, retrieving relevant context, then generating an answer from that context.

## AgentWorkflow

AgentWorkflow is a higher-level workflow for agents. Instead of manually writing every step and event, you define tools and agents. The agent decides which tool to call and can store shared state through Context.
