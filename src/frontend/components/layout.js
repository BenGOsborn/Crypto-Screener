import Head from 'next/head';
import Header from './header';

export default function Layout(props) {
    return (
        <>
            <Head>
                <title>CryptoScreener</title>
                <meta name="description" content="Ranks crypto tokens based on their price changes, volume, and volume abnormality to help you find the ones that are performing the best!" />
                <meta name="keywords" content="crypto, screener, cryptoscreener, tokens, finance, cryptocurrency" />
                <meta name="viewport" content="width=device-width,initial-scale=1.0" />
            </Head>

            <Header />
            <br />
            {props.children}
        </>
    );
}