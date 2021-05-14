import React from 'react';
import axios from 'axios';

// Different options to get the items for different pages and rank by different amounts and such
function loadPageData(pageNum, reverse, debug=false) {
    axios.post('https://coin-screener-api.herokuapp.com/api/get_page', { page_number: pageNum, reverse: reverse })
    .then(res => {
        const form = res.data;

        return form.data;
    })
    .catch(err => {
        const form = err.response;

        if (debug === true) {
            console.log(form);
        }

        return null;
    });
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

    return (
        <div>
            {/* I need to add headings and titles to my table of course */}
            {/* Change the colours of the numbers - also round them */}
            {pageData.map(row => {
                return (
                    <tr>
                        {/* Dynamically resize these images */}
                        <td><img src={row.token_info.image} width={25} height={25} /></td>
                        <td>{row.token_info.name}</td>
                        <td><a href={row.token_info.url}>{row.token_info.symbol}</a></td>
                        {console.log(row.price_data)}
                        {row.price_data.map(price => {
                            let colour;
                            if (price < 0) {
                                colour = "text-danger";
                            } else if (price > 0) {
                                colour = "text-success";
                            } else {
                                colour = "";
                            }
                            return (
                                <td className={colour}>{parseInt(price * 100) / 100}</td>
                            );
                        })}
                    </tr>
                );
            })}
        </div>
    );
}