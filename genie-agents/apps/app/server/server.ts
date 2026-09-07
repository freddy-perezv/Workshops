import { analytics, createApp, genie, server } from '@databricks/appkit';
import { setupDecisionRoutes } from './routes/decision-routes';

createApp({
  plugins: [
    analytics({
      warehouseStartupTimeoutMs: 300_000,
      autoStartWarehouse: true,
    }),
    genie({
      spaces: {
        'pulso-retail': process.env.DATABRICKS_GENIE_SPACE_ID ?? '',
      },
    }),
    server(),
  ],
  async onPluginsReady(appkit) {
    setupDecisionRoutes(appkit);
  },
}).catch((error) => {
  console.error('[pulso-retail] Unable to start application', error);
  process.exitCode = 1;
});
