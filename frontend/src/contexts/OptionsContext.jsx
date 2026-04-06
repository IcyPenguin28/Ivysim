import { createContext, useContext, useState } from "react";

const OptionsContext = createContext();

export function OptionsProvider({children}) {
    const [trainerName, setTrainerName] = useState("RED");
    const [rivalName, setRivalName] = useState("BLUE");
    const [numBattles, setNumBattles] = useState(250);

    return (
        <OptionsContext.Provider value={{ trainerName, setTrainerName, rivalName, setRivalName, numBattles, setNumBattles }}>
            {children}
        </OptionsContext.Provider>
    );
}

export function useOptions() {
    return useContext(OptionsContext);
}