import React, { Component } from "react";

class Header extends Component {
  render() {
    return (
      <div className="text-center">
        <img
          src={"/static/rare-disease-day-logo.jpeg"}
          className="img-thumbnail"
          style={{ marginTop: "20px", maxWidth: "30%" }}
        />
        <hr />
        <h1>Rare Disease Symptom Checker</h1>
      </div>
    );
  }
}

export default Header;