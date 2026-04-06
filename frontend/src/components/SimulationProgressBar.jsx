import "../css/SimulationProgressBar.css"

function SimulationProgressBar({currBattle=0, numBattles, progress}) {
    return (
        <div className="hpBarContainer">
            <div className="hpBarFill" style={{width: `${progress * 144}px`}}/>
            <div className="hpValues">{currBattle} / {numBattles}</div>
        </div>
    )
}

export default SimulationProgressBar