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

const tableTextStyle = {
    textDecoration: 'none',
    color: 'black'
}

export default function CoinScreener() {
    const [pageInfo, setPageInfo] = React.useState({'pageMin': null, 'pageMax': null, 'pageSize': 0, 'numSymbols': 0})
    const [page, setPage] = React.useState(1);
    const [reverse, setReversed] = React.useState(false);
    const [pageData, setPageData] = React.useState([]);
    const [error, setError] = React.useState(false);

    React.useEffect(() => {
        axios.get('https://coin-screener-api.herokuapp.com/api/get_pages_info')
        .then(res => {
            const form = res.data;
            
            setPageInfo(form); // Do one of these on every page load
            setError(false);
        })
        .catch(err => {
            const form = err.response;

            setError(true);
        });
    }, []);

    React.useEffect(() => {
        axios.post('https://coin-screener-api.herokuapp.com/api/get_page_data', { pageNumber: page, reverse: reverse == "true" })
        .then(res => {
            const form = res.data;

            setPageData(form); 
            setError(false);
        })
        .catch(err => {
            const form = err.response;

            console.log(form);

            setError(true);
        });
    }, [page, reverse]);

    // Also handle the loading errors here
    function pagination() {
        return (
            <ul className="pagination">
                <li className={`page-item ${page === pageInfo.pageMin ? "disabled" : ""}`}><a className="page-link" href="#" onClick={() => setPage(page - 1) ? page > pageInfo.pageMin : null}>Previous</a></li>

                {/* Make it so this cant break when there arent any coins loaded in */}
                {/* I need to disable them if they are active also */}

                <li className={`page-item ${page == pageInfo.pageMin ? "active" : ""}`}><a className="page-link" href="#" onClick={e => setPage(page === pageInfo.pageMin ? page : page === pageInfo.pageMax ? page - 2 : page - 1)}>{page === pageInfo.pageMin ? page : page === pageInfo.pageMax ? page - 2 : page - 1}</a></li>
                <li className={`page-item ${page > pageInfo.pageMin && page < pageInfo.pageMax ? "active" : ""}`}><a className="page-link" href="#" onClick={e => setPage(page === pageInfo.pageMin ? page + 1 : page === pageInfo.pageMax ? page - 1 : page)}>{page === pageInfo.pageMin ? page + 1 : page === pageInfo.pageMax ? page - 1 : page}</a></li>
                <li className={`page-item ${page == pageInfo.pageMax ? "active" : ""}`}><a className="page-link" href="#" onClick={e => setPage(page === pageInfo.pageMin ? page + 2 : page === pageInfo.pageMax ? page : page + 1)}>{page === pageInfo.pageMin ? page + 2 : page === pageInfo.pageMax ? page : page + 1}</a></li>

                <li className={`page-item ${page === pageInfo.pageMax ? "disabled" : ""}`}><a className="page-link" href="#" onClick={() => setPage(page + 1) ? page < pageInfo.pageMax : null}>Next</a></li>
            </ul>
        );
    }

    return (
        <div className="CoinScreener">

            <div className="container">
                <div className="row">

                    <select className="form-select col" onChange={e => setReversed(e.target.value)}>
                        <option value={false}>Best performing</option>
                        <option value={true}>Worst performing</option>
                    </select>

                    <span className="col">
                        {pagination()}
                    </span>

                </div>
            </div>

            <br />

            <table className="table">
                <thead className="thead-dark">
                    <tr>
                        <th>#</th>
                        <th>Token image</th>
                        <th>Token name</th>
                        <th>Token symbol</th>
                        <th>Token 2hr % change</th>
                        <th>Token 6hr % change</th>
                        <th>Token 12hr % change</th>
                        <th>Token 24hr % change</th>
                        <th>Token 48hr % change</th>
                        <th>Token price ($USD)</th>
                        <th>24h token volume ($USD)</th>
                    </tr>
                </thead>
                <tbody>
                    {pageData.map(row => {
                        return (
                            <tr>
                                {/* Index, id, symbol, name, url, image, 2hr, 6hr, 12hr, 24hr, 48hr, recent price, moon score */}

                                <th scope="row">{row[0]}</th>

                                {/* Can I get my images to dynamically rescale */}
                                <td><a href={row[4]} target="_blank"><img src={row[5]} alt={row[2]} width={50} height={50} /></a></td> 
                                <td><a href={row[4]} target="_blank" style={tableTextStyle}>{row[3]}</a></td>
                                <td><a href={row[4]} target="_blank" style={tableTextStyle}>{row[2].toUpperCase()}</a></td>

                                <td className={chooseColour(row[6])}>{row[6]}</td>
                                <td className={chooseColour(row[7])}>{row[7]}</td>
                                <td className={chooseColour(row[8])}>{row[8]}</td>
                                <td className={chooseColour(row[9])}>{row[9]}</td>
                                <td className={chooseColour(row[10])}>{row[10]}</td>

                                <td>{row[11]}</td>
                                <td>{row[12]}</td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
            
        </div>
    );
}