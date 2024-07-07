import React from "react";
const Footer: React.FC = () => {
  return (
    <>
      <footer className="fixed bottom-0 left-0 w-full bg-black text-white py-4 text-center">
        <p>
          Maintained by{" "}
          <strong>
            <a
              target="_blank"
              href="https://metakgp.github.io/"
              className="text-white"
            >
              <strong>MetaKGP </strong>
            </a>
          </strong>
          with<strong> ❤️ and &lt;/&gt; </strong>at{" "}
          <a
            target="_blank"
            href="https://github.com/metakgp/gyfe"
            className="text-white"
          >
            <strong>GitHub</strong>
          </a>
        </p>
      </footer>
    </>
  );
};
export default Footer;
