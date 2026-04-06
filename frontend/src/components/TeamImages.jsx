import PokemonImage from "./PokemonImage"
import "../css/TeamImages.css"
import { useEffect, useState } from "react";
import { getEnemyTeam } from "../services/api";
import { usePlayerTeam } from "../contexts/PlayerTeamContext";

function TeamImages({ side, tid = "" }) {
    const { team: playerTeam } = usePlayerTeam();
    const [team, setTeam] = useState([]);

    useEffect(() => {
        async function fetchTeam() {
            if (!tid) {
                // Player team
                setTeam(playerTeam);
                return;
            }
            
            // Ememy team
            const data = await getEnemyTeam(tid);
            setTeam(data);
        }

        fetchTeam();
    }, [tid, playerTeam]);

    return (
        <div className="img-column" id={side}>
            {Array.from({ length: 6 }).map((_, i) => (
                <PokemonImage key={i} slot={i} team={team} belongsToPlayer={team === playerTeam ? true : false} />
            ))}
        </div>
    );
}

export default TeamImages