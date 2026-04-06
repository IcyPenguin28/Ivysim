import { useOptions } from "../contexts/OptionsContext";
import { usePlayerTeam } from "../contexts/PlayerTeamContext";
import { postSimulation, getSimulationProgress } from "../services/api";
import { useState, useEffect } from "react";
import SimulationProgressBar from "./SimulationProgressBar";
import SimulationResults from "./SimulationResults"

function BeginSimulationButton({ tid, onResults }) {
    const { team: playerTeam } = usePlayerTeam();
    const { 
        trainerName, 
        rivalName, 
        numBattles 
    } = useOptions();

    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currBattle, setCurrBattle] = useState(0);

    const data = {
        playerTeam: playerTeam,
        playerName: trainerName,
        enemyID: tid,
        rivalName: rivalName,
        numBattles: numBattles
    }

    async function pollProgress() {
        const interval = setInterval(async () => {
            try {
                const data = await getSimulationProgress();
                setProgress(data.progress);
                setCurrBattle(data.current);

                if (data.progress >= 1) {
                    setProgress(0);
                    setCurrBattle(0);
                    clearInterval(interval);
                }
            } catch (err) {
                console.error(err);
                clearInterval(interval)
            }
        }, 300);

        return interval;
    }

    async function handleBeginSim() {
        var interval = null;
        console.log("Submitting data:", data);
        try {
            setLoading(true);
            interval = pollProgress();
            const simResults = await postSimulation(data);
            onResults(simResults);
            // console.log(results);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
            clearInterval(interval);
        }
    }

    return (
        <>
            <button onClick={() => handleBeginSim()} disabled={loading}>Begin Simulation</button>
            <SimulationProgressBar currBattle={currBattle} progress={progress} numBattles={numBattles} />
        </>
    );
}

export default BeginSimulationButton