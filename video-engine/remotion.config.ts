import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 300 seconds to handle large public dirs with image sequences
Config.setDelayRenderTimeoutInMilliseconds(300000);

// Use 2 concurrent threads on CI for faster render (GitHub runners have 2 vCPUs)
Config.setConcurrency(2);
