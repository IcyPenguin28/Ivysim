import "../css/SimulationResults.css"
import { useState, useEffect } from "react"
import CUSTOMAPI_BASE_URL from "../services/api"

function SimulationResults({resultsData}) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        setVisible(resultsData ? true : false);
    }, [resultsData]);

    function downloadLogs() {
        const filename = resultsData.log_file;

        const url = `${CUSTOMAPI_BASE_URL}/download-log?f=${filename}`;

        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    return (visible &&
        <div className="resultsOverlay">
            <div className="resultsContainer">
                <div className="resultsText">
                    <h2>RESULTS</h2>
                    <ul>
                        <li>Overall Win Rate: {resultsData.overall_win_rate} Percent</li>
                        <li>Best Lead: {resultsData.best_lead}, Win Rate: {resultsData.best_win_rate} Percent</li>
                    </ul>
                </div>
                <div className="resultsButtons">
                    <button onClick={() => downloadLogs()}>Download Battle Logs</button>
                    <button onClick={() => setVisible(false)}>OK</button>
                </div>
            </div>
        </div>
        
    );
}

export default SimulationResults