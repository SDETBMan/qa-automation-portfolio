function fn() {
  var env = karate.env; // get system property 'karate.env'
  karate.log('karate.env system property was:', env);

  if (!env) {
    env = 'dev';
  }

  var config = {
    env: env,
    baseUrl: 'https://jsonplaceholder.typicode.com',
    connectTimeout: 5000,
    readTimeout: 10000
  };

  if (env === 'dev') {
    // default — JSONPlaceholder public API
  } else if (env === 'staging') {
    config.baseUrl = 'https://jsonplaceholder.typicode.com';
  } else if (env === 'prod') {
    config.baseUrl = 'https://jsonplaceholder.typicode.com';
  }

  // global request timeout configuration
  karate.configure('connectTimeout', config.connectTimeout);
  karate.configure('readTimeout', config.readTimeout);

  // global headers applied to every request
  karate.configure('headers', { 'Accept': 'application/json' });

  // logging configuration
  karate.configure('logPrettyRequest', true);
  karate.configure('logPrettyResponse', true);

  return config;
}
