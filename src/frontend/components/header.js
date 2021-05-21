import React from 'react';

export default function Header() {
    return (
        <div className="Header">

            <div className="text-center">
                <h1 style={{fontSize: 65}}>TOKENSPOT</h1>
                <h2>Crypto tools to save you time and maximize your gains!</h2>
                <p className="text-danger">*NOTHING ON THIS WEBSITE SHOULD BE TAKEN AS FINANCIAL ADVICE. WE ARE NOT RESPONSIBLE FOR ANY MONEY YOU MAY LOSE.*</p>
            </div>

            <nav class="navbar navbar-expand navbar-dark bg-dark">
                <div className="container">
                    <div class="collapse navbar-collapse">
                        <ul class="navbar-nav mx-auto">
                            <li class="nav-item"><a class="nav-link" href="#">COIN SCREENER</a></li>
                            <li class="nav-item"><a class="nav-link" href="#">HOT DISCUSSED COINS</a></li>
                            <li class="nav-item"><a class="nav-link" href="#">MORE COMING SOON...</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
        </div>
    );
}