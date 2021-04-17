import React, { Component } from "react";

class Header extends Component {
  render() {
    return (
      <div className="text-center">
        <img
          src="https://i2.wp.com/directorsblog.nih.gov/wp-content/uploads/2014/02/rare-disease-day-logo.jpg"
          width="300"
          className="img-thumbnail"
          style={{ marginTop: "20px" }}
        />
        <hr />
        <h1>Rare Disease Symptom Checker</h1>
      </div>
    );
  }
}

export default Header;