/*global module*/

const SECTION = 'rhel';
const routes = {};

routes[`/api/inventory`] = { host: `http://localhost:8082` };
routes[`/api/system-baseline`] = { host: `http://localhost:8083` };
routes[`/api/drift`] = { host: `http://localhost:8084` };
routes[`/api/historical-system-profiles`] = { host: `http://localhost:8085` };

module.exports = { routes };
