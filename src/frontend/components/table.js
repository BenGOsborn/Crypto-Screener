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
    const [pageInfo, setPageInfo] = React.useState({'page_min': null, 'page_max': null, 'page_size': 50})
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
        axios.post('https://coin-screener-api.herokuapp.com/api/get_page', { page_number: page, reverse: reverse })
        .then(res => {
            const form = res.data;

            setPageData(form.data); 
            setError(false);
        })
        .catch(err => {
            const form = err.response;

            setError(true);
        });
    }, [page]);

    // Now I need some way of navigating the different pages

    return (
        <table className="table">
            <thead className="thead-dark">
                <tr>
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
                            {/* Dynamically resize these images */}
                            {/* THE TOKEN PRICE AND THE MOON SCORE SHOULD NOT BE MULTIPLED BY 100 */}
                            <td><a href={row.token_info.url}><img src={row.token_info.image} width={25} height={25} /></a></td>
                            <td><a href={row.token_info.url}>{row.token_info.name}</a></td>
                            <td><a href={row.token_info.url}>{row.token_info.symbol}</a></td>
                            {row.price_data.slice(0, -2).map(price => {
                                return (
                                    <td className={chooseColour(price)}>{parseInt(price * 100)}</td>
                                );
                            })}
                            <td>{parseInt(row.price_data[5] * 1000000) / 1000000}</td>
                        </tr>
                    );
                })}
            </tbody>
        </table>
    );
}