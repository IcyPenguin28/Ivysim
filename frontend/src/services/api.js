const POKEAPI_BASE_URL = "http://pokeapi.co/api/v2"
const CUSTOMAPI_BASE_URL = "http://127.0.0.1:8000"

export const getPokemonArt = async(pokemon_name) => {
    // Edge cases, make value match
    if (pokemon_name === "mr. mime") pokemon_name = "mr-mime";
    if (pokemon_name === "farfetch'd") pokemon_name = "farfetchd";

    const response = await fetch(`${POKEAPI_BASE_URL}/pokemon/${pokemon_name}`);
    const data = await response.json();

    return (
        data?.sprites?.other?.["official-artwork"]?.front_default ||
        data?.sprites?.front_default ||  // fallback
        null
    );
};

export const getEnemyTeam = async(trainer_id) => {
    const response = await fetch(`${CUSTOMAPI_BASE_URL}/trainer/${trainer_id}`);
    const data = await response.json();
    return data.team;
};

export const getAllTrainers = async() => {
    const response = await fetch(`${CUSTOMAPI_BASE_URL}/trainers`);
    const data = await response.json();
    return data;
};

export const getAllPokemonNames = async() => {
    const response = await fetch(`${CUSTOMAPI_BASE_URL}/pokemon`);
    const data = await response.json();
    
    const keys = Object.keys(data);
    // console.log(keys);
    return keys;
};

export const getAllMoves = async() => {
    const response = await fetch(`${CUSTOMAPI_BASE_URL}/moves`);
    const data = await response.json();
    return data;
};

export const uploadSaveFile = async(file) => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${CUSTOMAPI_BASE_URL}/load-save`, {
        method: "POST",
        body: formData,
    })

    if (!response.ok) {
        throw new Error("Failed to parse save file")
    }

    const data = await response.json();
    return data;
};

export const postSimulation = async (data) => {

    // Normalize party and move slots
    const filteredTeam = data.playerTeam.filter(m => m !== null);
    const normalizedTeam = filteredTeam.map(mon => ({
        ...mon,
        moves: mon.moves.map(m => m.toLowerCase())
    }));

    const response = await fetch(`${CUSTOMAPI_BASE_URL}/simulate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            player_team: normalizedTeam,
            player_name: data.playerName,
            rival_name: data.rivalName,
            enemy_trainer_id: data.enemyID,
            num_battles: data.numBattles,
        }),
    });

    if (!response.ok) {
        throw new Error("Failed to begin simulation");
    }

    return await response.json();
};

export const getSimulationProgress = async() => {
    const response = await fetch(`${CUSTOMAPI_BASE_URL}/simulation-progress`);
    const data = response.json();
    return data;
};

export default CUSTOMAPI_BASE_URL;