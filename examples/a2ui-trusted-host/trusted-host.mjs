import {A2uiMessageSchema, Catalog, MessageProcessor} from '@a2ui/web_core/v0_9';
import {BASIC_COMPONENTS} from '@a2ui/web_core/v0_9/basic_catalog';

const BASIC_CATALOG_ID = 'https://a2ui.org/specification/v0_9/catalogs/basic/catalog.json';

export function createTrustedHost({allowedActions = [], onAction = () => {}} = {}) {
  const catalog = new Catalog(BASIC_CATALOG_ID, BASIC_COMPONENTS);
  const processor = new MessageProcessor([catalog], onAction, {version: 'v0.9.1'});
  const actionAllowlist = new Set(allowedActions);
  const acceptedMessages = [];

  return {
    process(messages) {
      for (const [index, message] of messages.entries()) {
        if (!A2uiMessageSchema.safeParse(message).success) {
          throw new Error(`Invalid A2UI message at index ${index}`);
        }
        for (const component of message.updateComponents?.components ?? []) {
          if (component.component && !catalog.components.has(component.component)) {
            throw new Error(`Untrusted component type: ${component.component}`);
          }
        }
      }
      const candidateMessages = structuredClone(messages);
      const stagingProcessor = new MessageProcessor([catalog], undefined, {version: 'v0.9.1'});
      stagingProcessor.processMessages(structuredClone(acceptedMessages));
      stagingProcessor.processMessages(candidateMessages);

      const committedMessages = structuredClone(messages);
      processor.processMessages(committedMessages);
      acceptedMessages.push(...structuredClone(committedMessages));
    },
    async dispatchAction(surfaceId, sourceComponentId, action) {
      const actionName = action?.event?.name;
      if (!actionAllowlist.has(actionName)) {
        throw new Error(`Untrusted action: ${actionName ?? '<missing>'}`);
      }
      const surface = processor.model.getSurface(surfaceId);
      if (!surface) throw new Error(`Surface not found: ${surfaceId}`);
      await surface.dispatchAction(action, sourceComponentId);
    },
    snapshot(surfaceId) {
      const surface = processor.model.getSurface(surfaceId);
      if (!surface) return null;

      return {
        components: Array.from(surface.componentsModel.entries, ([id, component]) => ({
          id,
          type: component.type,
        })),
        dataModel: surface.dataModel.get('/'),
      };
    },
  };
}
