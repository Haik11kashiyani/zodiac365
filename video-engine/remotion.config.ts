import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Increase timeout for slow CI environments (GitHub Actions)
// Video seeking can take 1-3 seconds per frame on headless runners
Config.setDelayRenderTimeoutInMilliseconds(90000);
