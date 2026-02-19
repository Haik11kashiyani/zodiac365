import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setCodec('h264');

// Timeout for slow CI environments (GitHub Actions)
// 3 minutes - generous safety net (font loading is now non-blocking via font-display:swap)
Config.setDelayRenderTimeoutInMilliseconds(600000);
