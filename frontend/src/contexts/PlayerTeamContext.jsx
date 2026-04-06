import { createContext, useContext, useState } from "react";

const PlayerTeamContext = createContext();

export function PlayerTeamProvider({children}) {
    const [team, setTeam] = useState([
        null, null, null, null, null, null
    ]);

    const setPokemonAtSlot = (slot, pokemon) => {
        setTeam(prev => {
            const newTeam = [...prev];
            newTeam[slot] = pokemon;
            console.log(newTeam);
            return newTeam;
        });
    };

    const getPokemonAtSlot = (slot) => {
        return team[slot];
    }

    return (
        <PlayerTeamContext.Provider value={{ team, setTeam, setPokemonAtSlot, getPokemonAtSlot }}>
            {children}
        </PlayerTeamContext.Provider>
    );
}

export function usePlayerTeam() {
    return useContext(PlayerTeamContext);
}