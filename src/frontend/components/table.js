import React from 'react';
import axios from 'axios';

function chooseColour(price) {
    if (price < 0) {
        return "text-danger";

    } else if (price > 0) {
        return "text-success";

    } else {
        return "";
    }
}

export default function Table() {
    const [pageInfo, setPageInfo] = React.useState({'pageMin': null, 'pageMax': null, 'pageSize': 0, 'numSymbols': 0})
    const [page, setPage] = React.useState(1);
    const [reverse, setReverse] = React.useState(false);
    const [pageData, setPageData] = React.useState([]);
    const [error, setError] = React.useState(false);

    React.useEffect(() => {
        axios.get('https://coin-screener-api.herokuapp.com/api/get_pages_info')
        .then(res => {
            const form = res.data;
            
            setPageInfo(form);
            setError(false);
        })
        .catch(err => {
            const form = err.response;

            setError(true);
        });
    }, []);

    React.useEffect(() => { // This should run initially too
        axios.post('https://coin-screener-api.herokuapp.com/api/get_page_data', { pageNumber: page, reverse: reverse })
        .then(res => {
            const form = res.data;

            // Index, id, symbol, name, url, image, 2hr, 6hr, 12hr, 24hr, 48hr, recent price, moon score
            console.log(form);

            setPageData(form); 
            setError(false);
        })
        .catch(err => {
            const form = err.response;

            console.log(form);

            setError(true);
        });
    }, [page, reverse]);

    // Now I need some way of navigating the different pages

    return (
        <table className="table">
            <thead className="thead-dark">
                <tr>
                    <th>Token rank</th>
                    <th>Token image</th>
                    <th>Token name</th>
                    <th>Token symbol</th>
                    <th>Token 2hr % change</th>
                    <th>Token 6hr % change</th>
                    <th>Token 12hr % change</th>
                    <th>Token 24hr % change</th>
                    <th>Token 48hr % change</th>
                    <th>Token price ($USD)</th>
                </tr>
            </thead>
            <tbody>
                {pageData.map(row => {
                    return (
                        <tr>
                            {row.map(col => {
                                return (
                                    <td>{col}</td>
                                );
                            })}
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}