import { useEffect, useState } from "react";
import { getAllMoves } from "../services/api"

function MoveSelector({ value, onChange, allMovesInSet }) {
    const [moveOptions, setMoveOptions] = useState([]); // Initialize as empty array
    const [open, setOpen] = useState(false);
    const [hoverIndex, setHoverIndex] = useState(null);

    useEffect(() => {
        const fetchNames = async () => {
            try {
                const moves = await getAllMoves();
                if (moves) {
                    const keys = Object.keys(moves);
                    setMoveOptions(["--", ...keys]);
                }
            } catch (err) {
                console.error("Failed to load moves", err);
                setMoveOptions(["--"]); // Fallback
            }
        }
        fetchNames();
    }, [])

    const handleSelect = (moveId) => {
        const newValue = moveId === "--" ? null : moveId;

        // Must have at least 1 learned move
        if (newValue === null) {
            const activeMoves = allMovesInSet.filter(m => m !== null && m !== "--");
            if (activeMoves.length <= 1 && value !== null) {
                alert("A Pokémon must have at least one move!");
                setOpen(false);
                return;
            }
        }

        onChange(newValue);
        setOpen(false);
    };

    const selectedLabel = (value === null || value === "--") ? "--" : value.toUpperCase();

    return (
        <div className="dropdown">
            <div className="dropdownSelected" onClick={() => setOpen(prev => !prev)}>
                <span>{selectedLabel}</span>
                <span className={`arrow ${open ? "up" : "down"}`} />
            </div>

            {open && (
                <div className="dropdownOptions">
                    {/* Safety check with optional chaining or ensuring it's an array */}
                    {Array.isArray(moveOptions) && moveOptions.map((id, index) => (
                        <div
                            key={id}
                            className="dropdownOption"
                            onMouseEnter={() => setHoverIndex(index)}
                            onMouseLeave={() => setHoverIndex(null)}
                            onClick={() => handleSelect(id)}
                        >
                            {hoverIndex === index && (<span className="optionArrow" />)}
                            {id.toUpperCase()}
                        </div>
                    ))}
                </div>
            )}
        </div>
    )
}

export default MoveSelector