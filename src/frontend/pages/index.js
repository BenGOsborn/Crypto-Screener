import { useEffect, useState, useRef } from "react";
import axios from "axios";
import styles from "../styles/CoinScreener.module.css";

// Sets the colour of the text through its class if the number given is positive or negative
function chooseColour(price) {
    if (price < 0) {
        return "textRed";
    } else {
        return "textGreen";
    }
}

// Formats the number in a more readable fashion e.g. representing a million as 1m or a billion as 1b
function parseNumber(number) {
    if (Math.abs(number) > 1e9) {
        return Math.round((100 * number) / 1e9) / 100 + "b";
    } else if (Math.abs(number) > 1e6) {
        return Math.round((100 * number) / 1e6) / 100 + "m";
    } else if (Math.abs(number) > 1e3) {
        return Math.round((100 * number) / 1e3) / 100 + "k";
    } else {
        return Math.abs(number) > 1
            ? Math.round(number * 100) / 100
            : number.toPrecision(2);
    }
}

export default function CoinScreener() {
    const [pageInfo, setPageInfo] = useState({
        pageMin: 1,
        pageMax: 3,
        pageSize: 0,
        numSymbols: 0,
    }); // Try and set the pageMax to be max(pageMax, 3)

    const [page, setPage] = useState(1);
    const pageRef = useRef(1); // Used for reading the state within the setInterval
    const [reverse, setReversed] = useState(false);
    const reverseRef = useRef(false); // Used for reading the state within the setInterval

    const [pageData, setPageData] = useState([]);
    const [loaded, setLoaded] = useState(false);

    // Continuously get the data for the page and reverse options specified by the user
    useEffect(() => {
        setInterval(() => {
            // Get token data for specified page with reversed option
            axios
                .post(
                    "https://coin-screener-api.herokuapp.com/api/get_page_data",
                    { pageNumber: pageRef.current, reverse: reverseRef.current }
                )
                .then((res) => {
                    const form = res.data;

                    setPageData(form);
                    setLoaded(true);
                })
                .catch((err) => {
                    const form = err.response;
                });

            // Update the request limits
            axios
                .get(
                    "https://coin-screener-api.herokuapp.com/api/get_pages_info"
                )
                .then((res) => {
                    const form = res.data;

                    setPageInfo(form);
                })
                .catch((err) => {
                    const form = err.response;
                });
        }, 15 * 1000);
    }, []);

    // Update the data for the specified page number and reversed whenever the page or order is changed
    useEffect(() => {
        // Get token data for specified page with reversed option
        axios
            .post("https://coin-screener-api.herokuapp.com/api/get_page_data", {
                pageNumber: page,
                reverse: reverse,
            })
            .then((res) => {
                const form = res.data;

                setPageData(form);
                setLoaded(true);
            })
            .catch((err) => {
                const form = err.response;

                setLoaded(false);
            });

        // Update the request limits
        axios
            .get("https://coin-screener-api.herokuapp.com/api/get_pages_info")
            .then((res) => {
                const form = res.data;

                setPageInfo(form);
            })
            .catch((err) => {
                const form = err.response;
            });
    }, [page, reverse]);

    function _setPage(e, newPage) {
        e.preventDefault();

        if (
            pageRef.current === newPage ||
            newPage > pageInfo.pageMax ||
            newPage < pageInfo.pageMin
        ) {
            return;
        }

        pageRef.current = newPage;
        setPage(newPage);
    }

    function _setReverse(e, newReversed) {
        e.preventDefault();

        if (reverseRef.current === newReversed) {
            return;
        }

        reverseRef.current = newReversed;
        setReversed(newReversed);
    }

    function paginationButton(buttonNumber) {
        if (buttonNumber !== -1 && buttonNumber !== 0 && buttonNumber !== 1) {
            console.error("buttonNumber must be '-1', '0', or '1'");
            return null;
        }

        let displayNumber = -1;

        if (page <= pageInfo.pageMin) {
            displayNumber = page + 1 + buttonNumber;
        } else if (page >= pageInfo.pageMax && pageInfo.pageMax > 2) {
            displayNumber = page - 1 + buttonNumber;
        } else {
            displayNumber = page + buttonNumber;
        }

        if (
            (buttonNumber === 0 && pageInfo.pageMax < 2) ||
            (buttonNumber === 1 && pageInfo.pageMax < 3)
        ) {
            return null;
        } else {
            if (displayNumber === page) {
                return (
                    <a
                        className={styles.active}
                        href="#"
                        onClick={(e) => _setPage(e, displayNumber)}
                    >
                        {displayNumber}
                    </a>
                );
            }

            return (
                <a href="#" onClick={(e) => _setPage(e, displayNumber)}>
                    {displayNumber}
                </a>
            );
        }
    }

    return (
        <div className="CoinScreener">
            {loaded ? ( // If the page has loaded display the standard layout
                <div className="container">
                    <div className={styles.tableWrapper}>
                        <table className={styles.contentTable}>
                            <thead>
                                <tr>
                                    <th>
                                        <a
                                            className="textWhite"
                                            href="#"
                                            onClick={(e) =>
                                                _setReverse(e, !reverse)
                                            }
                                        >
                                            {reverse ? (
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    fill="currentColor"
                                                    className="bi bi-arrow-up"
                                                    viewBox="0 0 16 16"
                                                >
                                                    <path
                                                        fillRule="evenodd"
                                                        d="M8 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L7.5 2.707V14.5a.5.5 0 0 0 .5.5z"
                                                    />
                                                </svg>
                                            ) : (
                                                <svg
                                                    xmlns="http://www.w3.org/2000/svg"
                                                    fill="currentColor"
                                                    className="bi bi-arrow-down"
                                                    viewBox="0 0 16 16"
                                                >
                                                    <path
                                                        fillRule="evenodd"
                                                        d="M8 1a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L7.5 13.293V1.5A.5.5 0 0 1 8 1z"
                                                    />
                                                </svg>
                                            )}
                                        </a>
                                    </th>
                                    <th>Token name</th>
                                    <th>Token 2hr change</th>
                                    {/* <th>Token 6hr change</th> */}
                                    {/* <th>Token 12hr change</th> */}
                                    <th>Token 24hr change</th>
                                    <th>Token 48hr change</th>
                                    <th>Token price ($USD)</th>
                                    <th>24h token volume ($USD)</th>
                                </tr>
                            </thead>
                            <tbody>
                                {pageData.map((row) => {
                                    return (
                                        <tr>
                                            {/* Row data meanings: Index, id, symbol, name, url, image, 2hr, 6hr, 12hr, 24hr, 48hr, recent price, moon score */}
                                            <th className="textLight">
                                                {row[0]}
                                            </th>
                                            <td>
                                                <span>
                                                    <a
                                                        href={row[4]}
                                                        target="_blank"
                                                    >
                                                        <img
                                                            src={row[5]}
                                                            alt={row[2]}
                                                        />
                                                    </a>
                                                </span>
                                                <span>
                                                    <a
                                                        className="textWhite"
                                                        href={row[4]}
                                                        target="_blank"
                                                    >
                                                        {row[3]}
                                                    </a>
                                                </span>
                                                <span>
                                                    <a
                                                        className="textLight"
                                                        href={row[4]}
                                                        target="_blank"
                                                    >
                                                        ({row[2].toUpperCase()})
                                                    </a>
                                                </span>
                                            </td>
                                            <td
                                                className={chooseColour(row[6])}
                                            >
                                                {parseNumber(row[6])}%
                                            </td>
                                            {/* <td className={chooseColour(row[7])}>{parseNumber(row[7])}%</td> */}
                                            {/* <td className={chooseColour(row[8])}>{parseNumber(row[8])}%</td> */}
                                            <td
                                                className={chooseColour(row[9])}
                                            >
                                                {parseNumber(row[9])}%
                                            </td>
                                            <td
                                                className={chooseColour(
                                                    row[10]
                                                )}
                                            >
                                                {parseNumber(row[10])}%
                                            </td>
                                            <td className="textWhite">
                                                ${parseNumber(row[11])}
                                            </td>
                                            <td className="textWhite">
                                                ${parseNumber(row[12])}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>

                    {/* I want some sort of disabled styling */}
                    <div className="container">
                        <div className={styles.pagination}>
                            {/* The problem is is it is greater than min it will set the pages to 0, it shouldnt do that */}

                            <a
                                className={
                                    page <= pageInfo.pageMin
                                        ? styles.inactive
                                        : ""
                                }
                                href="#"
                                onClick={(e) => _setPage(e, pageInfo.pageMin)}
                            >
                                Start
                            </a>

                            <a
                                className={
                                    page <= pageInfo.pageMin
                                        ? styles.inactive
                                        : ""
                                }
                                href="#"
                                onClick={(e) => _setPage(e, page - 1)}
                            >
                                Previous
                            </a>

                            {paginationButton(-1)}
                            {paginationButton(0)}
                            {paginationButton(1)}

                            <a
                                className={
                                    page >= pageInfo.pageMax
                                        ? styles.inactive
                                        : ""
                                }
                                href="#"
                                onClick={(e) => _setPage(e, page + 1)}
                            >
                                Next
                            </a>

                            <a
                                className={
                                    page >= pageInfo.pageMax
                                        ? styles.inactive
                                        : ""
                                }
                                href="#"
                                onClick={(e) => _setPage(e, pageInfo.pageMax)}
                            >
                                End
                            </a>
                        </div>
                    </div>

                    <br />
                </div>
            ) : (
                // If the page has not loaded displaying a loading message
                <div>
                    <div className={styles.padContainer}>
                        <h1>Loading, this may take a minute</h1>
                    </div>
                </div>
            )}
        </div>
    );
}
