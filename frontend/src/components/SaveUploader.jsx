import { uploadSaveFile } from '../services/api';
import { usePlayerTeam } from '../contexts/PlayerTeamContext';

function SaveUploader({onNamesParsed}) {
    const { setTeam } = usePlayerTeam();

    const handleFileChange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        try {
            const data = await uploadSaveFile(file);
            
            const newTeam = [null, null, null, null, null, null];
            data.team.forEach((pokemon, index) => {
                if (index < 6) newTeam[index] = pokemon;
            });

            setTeam(newTeam);

            if (onNamesParsed) {
                onNamesParsed(data.trainer_name, data.rival_name)
            }

            alert(`Loaded team for Trainer ${data.trainer_name}`);
        } catch (err) {
            console.error(err);
            alert("Error loading save file.");
        }
    };

    return (
        <div className="saveImporter">
            <label>Import Party From Save File: </label> <br/>
            <input type="file" onChange={handleFileChange} accept=".sav" />
        </div>
    );
}

export default SaveUploader