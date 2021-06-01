import React from 'react';

export default function Header() {
    return (
        <div className="Header">

            <div className="text-center">
                <h1 style={{fontSize: 65, color: 'white'}}>TOKENSPOT</h1>
                <h2>Crypto tools to save you time and maximize your gains!</h2>
                <p className="text-danger">*NOTHING ON THIS WEBSITE SHOULD BE TAKEN AS FINANCIAL ADVICE. WE ARE NOT RESPONSIBLE FOR ANY MONEY YOU MAY LOSE.*</p>
            </div>

            <nav class="navbar navbar-expand navbar-dark bg-dark">
                <div className="container">
                    <div className="collapse navbar-collapse">
                        <ul className="navbar-nav mx-auto">
                            <li className="nav-item"><a className="nav-link" href="#">COIN SCREENER</a></li>
                            <li className="nav-item"><a className="nav-link" href="#">HOT DISCUSSED COINS</a></li>
                            <li className="nav-item"><a className="nav-link" href="#">MORE COMING SOON...</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
        </div>
    );
}