import CoinScreener from '../components/coinScreener';

export default function Main() {
  return (
    <div className="Main">

      <main>
        <div className="container">

          <div className="text-center">
            <h1>Coin Screener</h1>
            <p>Never miss out on the next coin boom again with a tool that ranks the best performing coins!</p>
          </div>

          <CoinScreener />

          
        </div>
      </main>

    </div>
  )
}
