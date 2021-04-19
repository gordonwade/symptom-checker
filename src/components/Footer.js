import React from "react";

const Footer = () => (
    <div className="footer">
        <p>This app is a proof of concept, and not intended for actual diagnostic purposes.</p>
        <div className="row">
            <div className="col-6 mx-auto p-0">
                <div className="row">
                    <div className="col">
                        <a href="mailto:gordonvwade@gmail.com"><i
                            className="fa fa-envelope fa-2x" aria-hidden="true"></i></a>
                    </div>
                    <div className="col">
                        <a href="http://github.com/gordonwade" target="_blank"><i
                            className="fa fa-github fa-2x" aria-hidden="true"></i></a>
                    </div>
                    <div className="col">
                        <a href="http://www.linkedin.com/in/gordonwade/" target="_blank"><i
                            className="fa fa-linkedin fa-2x" aria-hidden="true"></i></a>
                    </div>
                </div>
            </div>
        </div>
    </div>
);

export default Footer;