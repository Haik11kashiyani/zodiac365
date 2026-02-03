import { Composition, staticFile } from 'remotion';
import { ZodiacComposition, ZodiacCompositionProps } from './Composition';
import './style.css'; 

export const RemotionRoot: React.FC = () => {
    return (
        <>
            <Composition
                id="ZodiacVideo"
                component={ZodiacComposition as any}
                durationInFrames={30 * 60} 
                fps={30}
                width={1080}
                height={1920}
                calculateMetadata={({ props }) => {
                    const typedProps = props as any as ZodiacCompositionProps;
                    return {
                        durationInFrames: typedProps.durationInFrames || (30 * 60),
                    };
                }}
                defaultProps={({
                    scriptText: "Example Script",
                    audioSrc: "",
                    captions: [],
                    images: [],
                    title: "Aries Daily Horoscope",
                    durationInFrames: 30 * 60
                } as any) as ZodiacCompositionProps}
            />
        </>
    );
};
