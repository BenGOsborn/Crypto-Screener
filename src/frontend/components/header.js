import React from 'react';
import styles from '../styles/Header.module.css';

export default function Header() {
    return (
        <div className="Header">

            <br />

            <div className="container">
                <div className={styles.header}>
                    <h1>COINSCREENER</h1>
                    <h2>By <a href="https://github.com/BenGOsborn" target="_blank" style={{color: 'inherit'}}>Ben Osborn</a></h2>
                    <h3>Ranks crypto tokens based on their price changes, volume, and volume abnormality to help you find what ones are performing the best!</h3>
                    <h4>NOTHING ON THIS WEBSITE SHOULD BE TAKEN AS FINANCIAL ADVICE. WE ARE NOT RESPONSIBLE FOR ANY MONEY YOU MAY LOSE.</h4>
                </div>
            </div>

        </div>
    );
}