import React from 'react';
import axios from 'axios';
import '../styles/CoinScreener.module.css';

function chooseColour(price) {
    if (price < 0) {
        return "text-red";

    } else if (price > 0) {
        return "text-green";

    } else {
        return "text-white";
    }
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
        axios.post('https://coin-screener-api.herokuapp.com/api/get_page_data', { pageNumber: page, reverse: reverse })
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

            <div className="text-center">
                {pagination()}
            </div>

            <table className="table">
                <thead className="thead-dark">
                    <tr className="text-white">
                        <th scope="col">
                            <a className="text-white" href="#" onClick={e => setReversed(!reverse)}>{reverse ? 
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-up" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 15a.5.5 0 0 0 .5-.5V2.707l3.146 3.147a.5.5 0 0 0 .708-.708l-4-4a.5.5 0 0 0-.708 0l-4 4a.5.5 0 1 0 .708.708L7.5 2.707V14.5a.5.5 0 0 0 .5.5z"/></svg> :
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-arrow-down" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L7.5 13.293V1.5A.5.5 0 0 1 8 1z"/></svg>}</a>
                        </th>
                        <th scope="col">Token image</th>
                        <th scope="col">Token name</th>
                        <th scope="col">Token symbol</th>
                        <th scope="col">Token 2hr % change</th>
                        <th scope="col">Token 6hr % change</th>
                        <th scope="col">Token 12hr % change</th>
                        <th scope="col">Token 24hr % change</th>
                        <th scope="col">Token 48hr % change</th>
                        <th scope="col">Token price ($USD)</th>
                        <th scope="col">24h token volume ($USD)</th>
                    </tr>
                </thead>
                <tbody>
                    {pageData.map(row => {
                        return (
                            <tr>
                                {/* Index, id, symbol, name, url, image, 2hr, 6hr, 12hr, 24hr, 48hr, recent price, moon score */}

                                <th scope="row" className="text-white">{row[0]}</th>

                                {/* Can I get my images to dynamically rescale */}
                                <td><a href={row[4]} target="_blank"><img src={row[5]} alt={row[2]} width={50} height={50} /></a></td> 
                                <td><a className="text-white" href={row[4]} target="_blank">{row[3]}</a></td>
                                <td><a className="text-white" href={row[4]} target="_blank">{row[2].toUpperCase()}</a></td>

                                <td className={chooseColour(row[6])}>{row[6]}</td>
                                <td className={chooseColour(row[7])}>{row[7]}</td>
                                <td className={chooseColour(row[8])}>{row[8]}</td>
                                <td className={chooseColour(row[9])}>{row[9]}</td>
                                {/* <td className={chooseColour(row[10])}>{row[10]}</td> */}
                                <td style={{color: 'green'}}>{row[10]}</td>

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