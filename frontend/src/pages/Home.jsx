import "../css/Home.css"
import TeamImages from "../components/TeamImages"
import TrainerRed from "../assets/images/red.png"
import Logo from "../assets/images/logo.svg"
import EnemyTrainerImage from "../components/EnemyTrainerImage"
import TrainerSelector from "../components/TrainerSelector"
import SaveUploader from "../components/SaveUploader"
import { useState } from "react"
import { useOptions } from "../contexts/OptionsContext";
import BeginSimulationButton from "../components/BeginSimulationButton"
import SimulationResults from "../components/SimulationResults"

function Home() {
  const [enemyID, setEnemyID] = useState("blue1g");
  const [simResults, setSimResults] = useState(null);

  const { 
    trainerName, setTrainerName, 
    rivalName, setRivalName, 
    numBattles, setNumBattles 
  } = useOptions();

  function guardedSetNumBattles(desiredValue) {
    if (desiredValue === "") {
            setNumBattles(""); // allow clearing input temporarily
            return;
        }
        const num = Number(desiredValue);

        if (isNaN(num)) return;

        setNumBattles(Math.min(10000, Math.max(1, num)));
  }

  return (
    <>
      <div className="logo">
        <img src={Logo} alt="Ivysim"></img>
      </div>
      <div className="teams">
        <TeamImages side={"player"}/>
        <TeamImages side={"enemy"} tid={enemyID}/>
      </div>
      <div className="trainers">
        <img src={TrainerRed} alt="RED" id="red"></img>
        <EnemyTrainerImage trainer_id={enemyID}/>
        <h2>VS.</h2>
        <TrainerSelector value={enemyID} onChange={setEnemyID}/>
      </div>
      <div className="battleOptions">
        <h4>Battle Options</h4><br/>
        <label>Player Name: </label>
        <input placeholder={"RED"} value={trainerName} maxLength={7} onChange={(e) => setTrainerName(e.target.value)}/>
        <label>Rival Name: </label>
        <input placeholder={"BLUE"} value={rivalName} maxLength={7} onChange={(e) => setRivalName(e.target.value)}/>
        <SaveUploader onNamesParsed={(player, rival) => {
          setTrainerName(player);
          setRivalName(rival);
        }} />
      </div>
      <div className="simulationOptions">
        <h4>Simulation Options</h4>
        <label>Number of Battles: </label>
        <input type="number" min={1} max={10000} placeholder={250} value={numBattles} onChange={(e) => guardedSetNumBattles(e.target.value)} />
        <BeginSimulationButton tid={enemyID} onResults={setSimResults} />
      </div>
      <SimulationResults resultsData={simResults} />
    </>
    
  )
}

export default Home