import React, {Component, Fragment} from "react";
import AlertModal from "./components/Modal";
import Footer from "./components/Footer";
import Header from "./components/Header";
import axios from "axios";
import {getCookie} from "./utils/cookies.js";
import {getRiskTier} from "./utils/dataProcessing.js";


class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            viewCompleted: false,
            selectionSymptoms: [],
            possibleDisorders: [],
            modal: false,
            diagnose: false,
        };
        this.showModal = this.showModal.bind(this);
        this.hideModal = this.hideModal.bind(this);
    }

    showModal = () => {
        this.setState({ modal: true });
    };

    hideModal = () => {
        this.setState({ modal: false });
    };

    componentDidMount() {
        this.refreshList();
    }

    refreshList = () => {
        axios
            .get("/api/symptoms/")
            .then((res) => {
                let selectionSymptoms = res.data;
                console.log(selectionSymptoms);
                selectionSymptoms.forEach((element) => {
                    element.selected = false;
                });
                console.log(selectionSymptoms);

                this.setState({selectionSymptoms: selectionSymptoms});
            })
            .catch((err) => console.log(err));
    };

    getMatches = () => {
        let symptomIds = this.getSelectedSymptomIds().join();
        const csrftoken = getCookie('csrftoken');
        const config = {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            }
        };

        const body = {
            'symptom_keys': symptomIds
        };
        axios
        // .get("/api/disorder?symptom_keys=" + symptomIds)
            .post("/api/disorder/", body, config)
            .then((res) => {
                let matchingDisorders = res.data;
                // console.log(matchingDisorders);
                this.setState({'possibleDisorders': matchingDisorders});
                console.log("State is set!")
            })
            .catch((err) => console.log(err));
    };

    toggleSymptom = (symptomId) => {
        let items = this.state.selectionSymptoms;
        items.forEach((item) => {
            if (item.id == symptomId) {
                item.selected = !item.selected;
            }
        });
        this.setState({'selectionSymptoms': items});
    };

    selectSymptom = (item) => {
        this.toggleSymptom(item.id);
        this.renderSymptoms();
        console.log("Getting selected symptoms...");
        console.log(this.getSelectedSymptoms());
        this.render();
    };

    resetButton = () => (
        <button
            className="btn btn-outline-dark mr-2"
            onClick={() => {
                this.setState({'diagnose': false});
                this.refreshList();
            }}
        >
            Reset
        </button>
    );


    renderSymptoms = () => {
        const selectionSymptoms = this.state.selectionSymptoms;

        // Create a set of buttons for the user to select symptoms from
        let symptomSelection = selectionSymptoms.map((item) => (
            <button
                key={item.term}
                className={item.selected == true ? "btn btn-primary mr-2" : "btn btn-outline-primary mr-2"}
                onClick={() => this.selectSymptom(item)}
            >
                {item.term}
            </button>
        ));

        return (
            <div>
                <h5>Please select the symptoms that affect you:</h5>
                <br/>
                <div className="row justify-content-center align-items-center">
                    <div className="btn-group-vertical border-top-0 align-content-center">
                        {symptomSelection}
                    </div>
                </div>
                <br/>
                <div className="row justify-content-center align-items-center">
                    <div className="btn-group">
                        <button
                            className="btn btn-success mr-2"
                            onClick={() => {
                                if (this.getSelectedSymptoms().length > 0) {
                                    this.getMatches();
                                    this.setState({'diagnose': true});
                                } else {
                                    this.showModal();
                                }
                            }}
                        >
                            Diagnose
                        </button>
                        {this.resetButton()}
                    </div>
                </div>
            </div>
        );
    };

    renderDisorders = () => {
        const possibleDisorders = this.state.possibleDisorders;

        let disorderCards = possibleDisorders.map((item) => {
            let riskTier = getRiskTier(item, this.getSelectedSymptoms());
            let riskClass = `risk-${riskTier.replace(' ', '').toLowerCase()}`;
            return (
                <div className="card my-3 p-3">
                    <div className={`card-header ${riskClass}`}>
                        Risk Level: {riskTier}
                    </div>
                    <div className="card-body">
                        <h5 className="card-title">{item.disorder_name}</h5>
                        <p className="card-text">{item.disorder_type_name}</p>
                        <p className="card-text">{item.disorder_group_name}</p>
                        <a href="#" className="btn btn-outline-primary disabled" aria-disabled="true">Learn More</a>
                    </div>
                </div>
            )
        });

        return (
            <div>
                <h5>The symptoms you selected may indicate the following disorders:</h5>
                {disorderCards}
                <br/>
                <div className="btn-group">
                    <button
                        className="btn btn-primary mr-2"
                        onClick={() => {
                            this.setState({'diagnose': false});
                        }}
                    >
                        Back to Symptom Selection
                    </button>
                    {this.resetButton()}
                </div>
            </div>
        )
    };

    getSelectedSymptoms = () => {
        return this.state.selectionSymptoms.filter(symptom => symptom.selected == true)
    };

    getSelectedSymptomIds = () => {
        return this.getSelectedSymptoms().map(entry => entry.id);
    };


    render() {
        const diagnosing = this.state.diagnose;
        let activePanel;
        if (diagnosing) {
            activePanel = this.renderDisorders()
        } else {
            activePanel = this.renderSymptoms()
        }

        return (
            <main className="container">
                <Header/>
                <div className="row justify-content-center align-items-center">
                    <div className="col-md-6 col-sm-10 mx-auto p-0">
                        {activePanel}
                    </div>
                </div>
                <AlertModal show={this.state.modal} handleClose={this.hideModal}>
                    <p>Modal</p>
                </AlertModal>
                <Footer/>
            </main>

        );
    }
}


export default App;