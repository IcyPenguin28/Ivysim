import { useState, useEffect } from "react";
import { getAllTrainers } from "../services/api";

const nameTable = {
    "blue1g": "BLUE, Oak's Lab (Bulbasaur)",
    "blue1f": "BLUE, Oak's Lab (Charmander)",
    "blue1w": "BLUE, Oak's Lab (Squirtle)",
    "blue2g": "BLUE, Route 22 No. 1 (Bulbasaur)",
    "blue2f": "BLUE, Route 22 No. 1 (Charmander)",
    "blue2w": "BLUE, Route 22 No. 1 (Squirtle)",
    "blue3g": "BLUE, Nugget Bridge (Bulbasaur)",
    "blue3f": "BLUE, Nugget Bridge (Charmander)",
    "blue3w": "BLUE, Nugget Bridge (Squirtle)",
    "blue4g": "BLUE, S.S. Anne (Bulbasaur)",
    "blue4f": "BLUE, S.S. Anne (Charmander)",
    "blue4w": "BLUE, S.S. Anne (Squirtle)",
    "blue5g": "BLUE, Pokémon Tower (Bulbasaur)",
    "blue5f": "BLUE, Pokémon Tower (Charmander)",
    "blue5w": "BLUE, Pokémon Tower (Squirtle)",
    "blue6g": "BLUE, Silph Co. (Bulbasaur)",
    "blue6f": "BLUE, Silph Co. (Charmander)",
    "blue6w": "BLUE, Silph Co. (Squirtle)",
    "blue7g": "BLUE, Route 22 No. 2 (Bulbasaur)",
    "blue7f": "BLUE, Route 22 No. 2 (Charmander)",
    "blue7w": "BLUE, Route 22 No. 2 (Squirtle)",
    "blue8g": "BLUE, Indigo League (Bulbasaur)",
    "blue8f": "BLUE, Indigo League (Charmander)",
    "blue8w": "BLUE, Indigo League (Squirtle)",
    "brock": "Leader BROCK",
    "misty": "Leader MISTY",
    "surge": "Leader LT. SURGE",
    "erika": "Leader ERIKA",
    "koga": "Leader KOGA",
    "sabrina": "Leader SABRINA",
    "blaine": "Leader BLAINE",
    "giovanni": "Leader GIOVANNI",
    "lorelei": "Elite LORELEI",
    "bruno": "Elite BRUNO",
    "agatha": "Elite AGATHA",
    "lance": "Elite LANCE"
}

function TrainerSelector({ value, onChange }) {
    const [trainerOptions, setTrainerOptions] = useState([]);
    const [open, setOpen] = useState(false);
    const [hoverIndex, setHoverIndex] = useState(null);

    useEffect(() => {
        const fetchNames = async () => {
            const names = []
            const trainers = await getAllTrainers();
            for (var i = 0; i < trainers.length; i++)
            {
                names.push(trainers[i].id);
            }

            setTrainerOptions(names);
        }

        fetchNames();
    }, [])

    const selectedLabel = nameTable[value];

    return (
        <div className="dropdown">
            <div className="dropdownSelected" onClick={() => setOpen(prev => !prev)}>
                <span>{selectedLabel}</span>
                <span className={`arrow ${open ? "up" : "down"}`} />
            </div>

            {open && (
                <div className="dropdownOptions">
                    {trainerOptions.map((id, index) => (
                        <div
                            key={id}
                            className="dropdownOption"
                            onMouseEnter={() => setHoverIndex(index)}
                            onMouseLeave={() => setHoverIndex(null)}
                            onClick={() => { onChange(id); setOpen(false); }}
                        >
                            {hoverIndex === index && (<span className="optionArrow" />)}
                            {nameTable[id]}
                        </div>
                    ))}
                </div>
                )}
        </div>
    );
}

export default TrainerSelector;