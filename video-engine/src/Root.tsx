import { Composition } from 'remotion';
import { ZodiacComposition } from './Composition';
import './style.css'; // We'll create this for fonts

export const RemotionRoot: React.FC = () => {
    return (
        <>
            <Composition
                id="ZodiacVideo"
                component={ZodiacComposition}
                durationInFrames={30 * 60} // Default 60s @ 30fps
                fps={30}
                width={1080}
                height={1920}
                defaultProps={{
                    scriptText: "Example Script",
                    audioSrc: "",
                    captions: [],
                    images: [],
                    title: "Aries Daily Horoscope"
                }}
            />
        </>
    );
};
