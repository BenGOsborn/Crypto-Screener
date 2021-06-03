import React from 'react';
import styles from '../styles/Header.module.css';

export default function Header() {
    return (
        <div className="Header">

            <div className={styles.disclaimer}>
                <h4>NOTHING ON THIS WEBSITE SHOULD BE CONSIDERED FINANCIAL ADVICE. I AM NOT RESPONSIBLE FOR ANY MONEY YOU MAY LOSE.</h4>
            </div>

            <br />

            <div className="container">
                <div className={styles.header}>
                    <h1>CRYPTOSCREENER</h1>
                    <h2>By <a href="https://github.com/BenGOsborn" target="_blank">Ben Osborn</a></h2>
                    <h3>Ranks crypto tokens based on their price changes, volume, and volume abnormality to help you find the ones that are performing the best!</h3>
                </div>
            </div>

        </div>
    );
}