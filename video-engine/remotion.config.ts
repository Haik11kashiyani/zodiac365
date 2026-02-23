import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 300 seconds to handle large public dirs with image sequences
Config.setDelayRenderTimeoutInMilliseconds(300000);

// Use single concurrency on CI to prevent memory pressure and
// the registerRoot race condition seen in multi-page renders
Config.setConcurrency(1);
