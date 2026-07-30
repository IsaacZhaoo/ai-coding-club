import assert from 'node:assert/strict';

import { Client, InMemoryTransport } from '@modelcontextprotocol/client';
import { McpServer } from '@modelcontextprotocol/server';
import * as z from 'zod/v4';

type Issue = {
  id: string;
  title: string;
  status: 'open' | 'closed';
};

const issues: Issue[] = [
  { id: 'ISSUE-001', title: 'Cache invalidation fails after deploy', status: 'open' },
  { id: 'ISSUE-002', title: 'Document the cache warming job', status: 'open' },
  { id: 'ISSUE-003', title: 'Remove the legacy webhook', status: 'closed' }
];

const server = new McpServer({ name: 'issue-tools', version: '1.0.0' });

server.registerTool(
  'issues.search',
  {
    title: 'Search issues',
    description:
      'Search the local issue index by words in the title. Use this before issues.close when the exact issue ID is unknown. This tool never changes issue state.',
    inputSchema: z.object({
      query: z.string().trim().min(2).max(80).describe('Two or more characters to match in the issue title'),
      status: z.enum(['open', 'closed', 'any']).default('open').describe('Which issue states to include')
    }),
    outputSchema: z.object({
      count: z.number().int().nonnegative(),
      issues: z.array(
        z.object({
          id: z.string(),
          title: z.string(),
          status: z.enum(['open', 'closed'])
        })
      )
    }),
    annotations: {
      readOnlyHint: true,
      openWorldHint: false
    }
  },
  async ({ query, status }) => {
    const normalizedQuery = query.toLowerCase();
    const matches = issues.filter(
      issue => issue.title.toLowerCase().includes(normalizedQuery) && (status === 'any' || issue.status === status)
    );
    const structuredContent = { count: matches.length, issues: matches };

    return {
      content: [
        {
          type: 'text',
          text:
            matches.length === 0
              ? 'No matching issues.'
              : matches.map(issue => `${issue.id} [${issue.status}] ${issue.title}`).join('\n')
        }
      ],
      structuredContent
    };
  }
);

server.registerTool(
  'issues.close',
  {
    title: 'Close an issue',
    description:
      'Close one issue by exact ID after the user has selected it. This changes stored issue state. Repeating the same call returns already_closed without another change.',
    inputSchema: z.object({
      issueId: z.string().regex(/^ISSUE-\d{3}$/).describe('Exact issue ID, for example ISSUE-002'),
      reason: z.string().trim().min(5).max(200).describe('Short reason recorded with the close action')
    }),
    outputSchema: z.object({
      issueId: z.string(),
      outcome: z.enum(['closed', 'already_closed']),
      status: z.literal('closed')
    }),
    annotations: {
      readOnlyHint: false,
      destructiveHint: true,
      idempotentHint: true,
      openWorldHint: false
    }
  },
  async ({ issueId }) => {
    const issue = issues.find(candidate => candidate.id === issueId);
    if (!issue) {
      return {
        isError: true,
        content: [
          {
            type: 'text',
            text: `Unknown issue ${issueId}. Call issues.search to find a valid issue ID, then retry.`
          }
        ]
      };
    }

    const outcome = issue.status === 'closed' ? 'already_closed' : 'closed';
    issue.status = 'closed';
    const structuredContent = { issueId, outcome, status: 'closed' as const };

    return {
      content: [
        {
          type: 'text',
          text: outcome === 'closed' ? `${issueId} is now closed.` : `${issueId} was already closed; no state changed.`
        }
      ],
      structuredContent
    };
  }
);

const client = new Client({ name: 'tool-design-verifier', version: '1.0.0' });
const [clientTransport, serverTransport] = InMemoryTransport.createLinkedPair();
await server.connect(serverTransport);
await client.connect(clientTransport);

const firstList = await client.listTools();
const secondList = await client.listTools();
const expectedOrder = ['issues.search', 'issues.close'];
assert.deepEqual(
  firstList.tools.map(tool => tool.name),
  expectedOrder
);
assert.deepEqual(
  secondList.tools.map(tool => tool.name),
  expectedOrder
);

const searchDefinition = firstList.tools.find(tool => tool.name === 'issues.search');
assert.equal(searchDefinition?.annotations?.readOnlyHint, true);
assert.equal(searchDefinition?.annotations?.openWorldHint, false);
assert.equal(
  (searchDefinition?.inputSchema.properties?.query as { description?: string } | undefined)?.description,
  'Two or more characters to match in the issue title'
);

const invalidSearchResult = (await client.callTool({
  name: 'issues.search',
  arguments: { query: 'c', status: 'open' }
})) as { isError?: boolean };
assert.equal(invalidSearchResult.isError, true);

const searchResult = (await client.callTool({
  name: 'issues.search',
  arguments: { query: 'cache', status: 'open' }
})) as { structuredContent?: { count: number; issues: Issue[] } };
assert.equal(searchResult.structuredContent?.count, 2);
assert.deepEqual(
  searchResult.structuredContent?.issues.map(issue => issue.id),
  ['ISSUE-001', 'ISSUE-002']
);

const missingResult = (await client.callTool({
  name: 'issues.close',
  arguments: { issueId: 'ISSUE-999', reason: 'Not reproducible' }
})) as { isError?: boolean; content?: Array<{ type: string; text?: string }> };
assert.equal(missingResult.isError, true);
assert.match(missingResult.content?.[0]?.text ?? '', /issues\.search/);

const closeResult = (await client.callTool({
  name: 'issues.close',
  arguments: { issueId: 'ISSUE-002', reason: 'Documentation completed' }
})) as { structuredContent?: { outcome: string } };
assert.equal(closeResult.structuredContent?.outcome, 'closed');

const repeatedCloseResult = (await client.callTool({
  name: 'issues.close',
  arguments: { issueId: 'ISSUE-002', reason: 'Documentation completed' }
})) as { structuredContent?: { outcome: string } };
assert.equal(repeatedCloseResult.structuredContent?.outcome, 'already_closed');
assert.equal(issues.find(issue => issue.id === 'ISSUE-002')?.status, 'closed');

console.log(
  JSON.stringify(
    {
      toolOrder: expectedOrder,
      invalidSchemaInputIsError: invalidSearchResult.isError,
      searchMatches: searchResult.structuredContent?.issues.map(issue => issue.id),
      missingIssueIsError: missingResult.isError,
      firstClose: closeResult.structuredContent?.outcome,
      repeatedClose: repeatedCloseResult.structuredContent?.outcome
    },
    null,
    2
  )
);

await client.close();
await server.close();
