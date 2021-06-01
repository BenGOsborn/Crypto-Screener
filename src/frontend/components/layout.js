import Head from 'next/head';
import Header from './header';

export default function Layout(props) {
    return (
        <>
            <Head>
            </Head>

            <Header />
            <br />
            {props.children}
        </>
    );
}