import React from 'react';
import { Composition, staticFile } from 'remotion';
import { ZodiacComposition } from './Composition';

// Font faces loaded via staticFile() — avoids webpack css-loader issues that
// can silently crash module evaluation and prevent registerRoot() from firing.
const FONT_FACES = [
    { family: 'Montserrat', weight: 400, file: 'fonts/Montserrat-Regular.woff2' },
    { family: 'Montserrat', weight: 700, file: 'fonts/Montserrat-Bold.woff2' },
    { family: 'Montserrat', weight: 800, file: 'fonts/Montserrat-ExtraBold.woff2' },
    { family: 'Montserrat', weight: 900, file: 'fonts/Montserrat-Black.woff2' },
    { family: 'Poppins', weight: 400, file: 'fonts/Poppins-Regular.woff2' },
    { family: 'Poppins', weight: 700, file: 'fonts/Poppins-Bold.woff2' },
    { family: 'Poppins', weight: 900, file: 'fonts/Poppins-Black.woff2' },
];

const fontCSS = FONT_FACES.map(f =>
    `@font-face { font-family: '${f.family}'; font-style: normal; font-weight: ${f.weight}; font-display: swap; src: url('${staticFile(f.file)}') format('woff2'); }`
).join('\n') + '\nbody { margin: 0; padding: 0; background: black; font-family: "Montserrat", sans-serif; }';

export const RemotionRoot: React.FC = () => {
    return (
        <>
            <style dangerouslySetInnerHTML={{ __html: fontCSS }} />
            <Composition
                id="ZodiacVideo"
                component={ZodiacComposition as React.FC<any>}
                durationInFrames={30 * 60} // Default 60s @ 30fps
                fps={30}
                width={1080}
                height={1920}
                defaultProps={{
                    scriptText: "Example Script",
                    audioSrc: "",
                    captions: [],
                    images: [],
                    title: "Aries Daily Horoscope",
                    durationInFrames: 1800,
                }}
                calculateMetadata={async ({ props }) => {
                    // Primary: read from meta.json (written by bridge.py to public/)
                    // This bypasses any Remotion --props serialization issues with
                    // the reserved 'durationInFrames' field.
                    let duration: number | undefined;
                    
                    try {
                        const resp = await fetch(staticFile('meta.json'));
                        if (resp.ok) {
                            const meta = await resp.json();
                            if (typeof meta.durationInFrames === 'number' && meta.durationInFrames > 0) {
                                duration = meta.durationInFrames;
                                console.log(`[calculateMetadata] from meta.json: ${duration} frames`);
                            }
                        }
                    } catch (e) {
                        console.warn('[calculateMetadata] meta.json fetch failed:', e);
                    }
                    
                    // Fallback: try props from --props=./input.json
                    if (!duration) {
                        const propDuration = (props as any).durationInFrames;
                        if (typeof propDuration === 'number' && propDuration > 0) {
                            duration = propDuration;
                            console.log(`[calculateMetadata] from props: ${duration} frames`);
                        }
                    }
                    
                    // Final fallback
                    if (!duration) {
                        duration = 30 * 60; // 60 seconds
                        console.warn(`[calculateMetadata] using default: ${duration} frames`);
                    }
                    
                    return { durationInFrames: duration };
                }}
            />
        </>
    );
};
