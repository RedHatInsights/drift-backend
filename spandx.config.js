/*global module*/

const SECTION = 'insights';
const APP_ID = 'drift';
const FRONTEND_PORT = 8002;
const routes = {};

// backend
routes[`/api/inventory`] = { host: `http://inventory-rest:8080` };
routes[`/api/system-baseline`] = { host: `http://system-baseline-rest:8080` };
routes[`/api/drift`] = { host: `http://drift-rest:8080` };
routes[`/api/historical-system-profiles`] = { host: `http://hsp-rest:8080` };

// frontend
routes[`/beta/${SECTION}/${APP_ID}`] = { host: `http://drift-frontend:${FRONTEND_PORT}` };
routes[`/${SECTION}/${APP_ID}`]      = { host: `http://drift-frontend:${FRONTEND_PORT}` };
routes[`/beta/apps/${APP_ID}`]       = { host: `http://drift-frontend:${FRONTEND_PORT}` };
routes[`/apps/${APP_ID}`]            = { host: `http://drift-frontend:${FRONTEND_PORT}` };


module.exports = { routes };
